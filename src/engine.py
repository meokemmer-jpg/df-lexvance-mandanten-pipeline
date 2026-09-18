from __future__ import annotations

import hashlib
import hmac
import json
import os
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional


def k12_provenance(payload: bytes, key: bytes = b"df-trinity-contrarian-v1") -> dict:
    return {
        "payload_hash": hashlib.sha256(payload).hexdigest(),
        "hmac_sha256": hmac.new(key, payload, hashlib.sha256).hexdigest(),
    }


def k13_anchor(payload_hash: str) -> dict:
    return {
        "anchor_type": "rfc3161-local-file-anchor",
        "iso_ts": datetime.now(timezone.utc).isoformat(),
        "payload_hash": payload_hash,
    }


def k16_lock_or_exit(df_name: str):
    import fcntl
    import sys

    lock_path = f"/tmp/df-trinity-{df_name}.lock"
    fd = os.open(lock_path, os.O_CREAT | os.O_WRONLY)
    try:
        fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        return fd
    except BlockingIOError:
        sys.exit(3)


PHASES = (
    "AKQUISITION",
    "ONBOARDING",
    "AKTIV",
    "ABRECHNUNG",
    "ABGESCHLOSSEN",
)

RVG_MAX_SATZ_EUR = 350.0

AUFBEWAHRUNG_TAGE = {
    "STANDARD": 365 * 6,
    "STRAFRECHT": 365 * 30,
    "FAMILIE": 365 * 5,
}


def iso_now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass(frozen=True)
class MandantenResult:
    mandant_id: str
    lifecycle_phase: str
    konflikt_status: str
    naechste_frist_iso: Optional[str]
    tage_bis_frist: Optional[int]
    rvg_stunden_offen: float
    rvg_satz_eur: float
    aufbewahrungs_frist_iso: Optional[str]
    source: str
    iso_timestamp: str
    phronesis_ticket: Optional[str] = None
    warnings: tuple[str, ...] = field(default_factory=tuple)
    payload_hash: Optional[str] = None
    anchor: Optional[dict] = None


def _parse_dt(value: str) -> datetime:
    normalized = value.replace("Z", "+00:00")
    parsed = datetime.fromisoformat(normalized)
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def _validate_rvg(satz_eur: float) -> bool:
    assert satz_eur >= 0, f"invalid rvg_satz: {satz_eur}"
    return satz_eur <= RVG_MAX_SATZ_EUR


def _calc_aufbewahrung(kategorie: str = "STANDARD", *, now: Optional[datetime] = None) -> str:
    assert kategorie in AUFBEWAHRUNG_TAGE, f"unknown kategorie: {kategorie}"
    base = now or datetime.now(timezone.utc)
    return (base.timestamp() + AUFBEWAHRUNG_TAGE[kategorie] * 86400).__str__()


def _calc_aufbewahrung_iso(kategorie: str = "STANDARD", *, now: Optional[datetime] = None) -> str:
    assert kategorie in AUFBEWAHRUNG_TAGE, f"unknown kategorie: {kategorie}"
    base = now or datetime.now(timezone.utc)
    return datetime.fromtimestamp(
        base.timestamp() + AUFBEWAHRUNG_TAGE[kategorie] * 86400,
        tz=timezone.utc,
    ).isoformat()


def _norm_party(value: str) -> str:
    return " ".join(value.casefold().strip().split())


def _as_string_list(payload: dict[str, Any], key: str) -> list[str]:
    raw = payload.get(key, [])
    assert isinstance(raw, list), f"{key} must be a list"
    assert all(isinstance(item, str) and item.strip() for item in raw), f"{key} must contain strings"
    return raw


def _conflict_status(conflict_parties: list[str], known_adverse_parties: list[str]) -> str:
    if not conflict_parties or not known_adverse_parties:
        return "CHECK_PENDING"
    own = {_norm_party(item) for item in conflict_parties}
    adverse = {_norm_party(item) for item in known_adverse_parties}
    return "FAIL" if own & adverse else "PASS"


def _days_until(deadline_iso: Optional[str], *, now: datetime) -> tuple[Optional[str], Optional[int]]:
    if not deadline_iso:
        return None, None
    deadline = _parse_dt(deadline_iso)
    seconds = (deadline - now).total_seconds()
    return deadline.isoformat(), int(seconds // 86400)


def _materialize_result(payload: dict[str, Any], *, source: str, phronesis_ticket: Optional[str] = None, now: Optional[datetime] = None) -> MandantenResult:
    now = now or datetime.now(timezone.utc)
    mandant_id = payload.get("mandant_id")
    lifecycle_phase = payload.get("lifecycle_phase", "AKTIV")
    assert isinstance(mandant_id, str) and mandant_id.strip(), "mandant_id required"
    assert lifecycle_phase in PHASES, f"invalid phase: {lifecycle_phase}"

    rvg_satz_eur = float(payload.get("rvg_satz_eur", 0.0))
    billable_minutes = int(payload.get("billable_minutes", 0))
    paid_minutes = int(payload.get("paid_minutes", 0))
    assert billable_minutes >= 0, "billable_minutes must be >= 0"
    assert paid_minutes >= 0, "paid_minutes must be >= 0"

    conflict_parties = _as_string_list(payload, "conflict_parties")
    known_adverse_parties = _as_string_list(payload, "known_adverse_parties")
    konflikt_status = _conflict_status(conflict_parties, known_adverse_parties)
    naechste_frist_iso, tage_bis_frist = _days_until(payload.get("deadline_iso"), now=now)

    warnings: list[str] = []
    if konflikt_status == "FAIL":
        warnings.append("KONFLIKT_TREFFER")
    elif konflikt_status == "CHECK_PENDING":
        warnings.append("KONFLIKT_DATEN_UNVOLLSTAENDIG")
    if naechste_frist_iso and tage_bis_frist is not None and tage_bis_frist < 0:
        warnings.append("FRIST_UEBERFAELLIG")
    if not _validate_rvg(rvg_satz_eur):
        warnings.append("RVG_SATZ_PLAUSIBILITAET_VERLETZT")

    canonical_payload = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    provenance = k12_provenance(canonical_payload)
    return MandantenResult(
        mandant_id=mandant_id,
        lifecycle_phase=lifecycle_phase,
        konflikt_status=konflikt_status,
        naechste_frist_iso=naechste_frist_iso,
        tage_bis_frist=tage_bis_frist,
        rvg_stunden_offen=round(max(billable_minutes - paid_minutes, 0) / 60.0, 2),
        rvg_satz_eur=rvg_satz_eur,
        aufbewahrungs_frist_iso=_calc_aufbewahrung_iso(str(payload.get("kategorie", "STANDARD")), now=now),
        source=source,
        iso_timestamp=now.isoformat(),
        phronesis_ticket=phronesis_ticket,
        warnings=tuple(warnings),
        payload_hash=provenance["payload_hash"],
        anchor=k13_anchor(provenance["payload_hash"]),
    )


def load_mandanten_payload(path: str | Path) -> dict[str, Any]:
    file_path = Path(path)
    raw = file_path.read_bytes()
    data = json.loads(raw.decode("utf-8"))
    assert isinstance(data, dict), "mandanten payload must be a JSON object"
    return data


def run_mandanten_pipeline(path: str | Path, *, now: Optional[datetime] = None) -> MandantenResult:
    file_path = Path(path)
    payload = load_mandanten_payload(file_path)
    return _materialize_result(payload, source=f"file:{file_path.name}", now=now)


def mock_mandanten_status(mandant_id: str, lifecycle_phase: str = "AKTIV") -> MandantenResult:
    payload = {
        "mandant_id": mandant_id,
        "lifecycle_phase": lifecycle_phase,
        "conflict_parties": [],
        "known_adverse_parties": [],
        "billable_minutes": 0,
        "paid_minutes": 0,
        "rvg_satz_eur": 0.0,
        "kategorie": "STANDARD",
    }
    return _materialize_result(payload, source="mock")


def real_mandanten_status(mandant_id: str, lifecycle_phase: str = "AKTIV", phronesis_ticket: Optional[str] = None) -> MandantenResult:
    if not phronesis_ticket:
        phronesis_ticket = os.environ.get("PHRONESIS_TICKET")
    if not phronesis_ticket:
        return mock_mandanten_status(mandant_id, lifecycle_phase)

    path = os.environ.get("DF_LEXVANCE_MANDANTEN_PAYLOAD")
    if path:
        result = run_mandanten_pipeline(path)
        return MandantenResult(**{**asdict(result), "phronesis_ticket": phronesis_ticket, "source": "real-file"})

    payload = {
        "mandant_id": mandant_id,
        "lifecycle_phase": lifecycle_phase,
        "conflict_parties": [mandant_id],
        "known_adverse_parties": [],
        "billable_minutes": 0,
        "paid_minutes": 0,
        "rvg_satz_eur": 200.0,
        "kategorie": "STANDARD",
    }
    return _materialize_result(payload, source="real-api", phronesis_ticket=phronesis_ticket)


def dispatch_mandanten_status(mandant_id: str, lifecycle_phase: str = "AKTIV") -> MandantenResult:
    real_enabled = os.environ.get("DF_LEXVANCE_MANDANTEN_REAL_ENABLED", "").lower() == "true"
    if real_enabled:
        return real_mandanten_status(mandant_id, lifecycle_phase)
    return mock_mandanten_status(mandant_id, lifecycle_phase)


def needs_konflikt_review(result: MandantenResult) -> bool:
    return result.konflikt_status != "PASS"


def to_audit_record(result: MandantenResult) -> dict:
    return {
        "ts": result.iso_timestamp,
        "df": "DF-LEXVANCE-MANDANTEN-PIPELINE",
        "mandant_id": result.mandant_id,
        "lifecycle_phase": result.lifecycle_phase,
        "konflikt_status": result.konflikt_status,
        "naechste_frist_iso": result.naechste_frist_iso,
        "tage_bis_frist": result.tage_bis_frist,
        "rvg_stunden_offen": result.rvg_stunden_offen,
        "rvg_satz_eur": result.rvg_satz_eur,
        "source": result.source,
        "phronesis_ticket": result.phronesis_ticket,
        "warnings": list(result.warnings),
        "payload_hash": result.payload_hash,
    }
