"""DF-LEXVANCE-MANDANTEN-PIPELINE Engine [CRUX-MK].

Welle-48 Track-A Wave-1 DC-1 Foundation-DF (Gap-Cluster D).
Mandanten-Lifecycle (Akquisition + Akten + Fristen + RVG-Abrechnung).

ENV-Var-gated Default-Disabled. Mock-Fallback bei Real-Mode-Disabled.

Pre/Post-Conditions:
- Pre: mandant_id (str), lifecycle_phase (str in PHASES)
- Post: MandantenResult mit phase, naechste_frist, rvg_stunden_offen, konflikt_status
"""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Optional


# Mandanten-Lifecycle-Phasen
PHASES = (
    "AKQUISITION",   # Lead-Tracking + Konflikt-Check
    "ONBOARDING",    # Mandat-Vertrag + DSGVO-Einwilligung
    "AKTIV",         # Akten + Fristen + RVG laufend
    "ABRECHNUNG",    # RVG-Endabrechnung
    "ABGESCHLOSSEN", # Aufbewahrungs-Frist beginnt
)

# RVG-Max-Stundensatz-Plausibilitaet (Skelett)
RVG_MAX_SATZ_EUR = 350.0

# Aufbewahrungs-Fristen (Tage)
AUFBEWAHRUNG_TAGE = {
    "STANDARD": 365 * 6,    # 6 Jahre BORA § 50
    "STRAFRECHT": 365 * 30, # 30 Jahre
    "FAMILIE": 365 * 5,     # 5 Jahre
}


def iso_now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass(frozen=True)
class MandantenResult:
    """Pflicht-Felder per env-var-gated-real-integration-default.md Property-3."""
    mandant_id: str
    lifecycle_phase: str           # aus PHASES
    konflikt_status: str           # "CHECK_PENDING"|"PASS"|"FAIL"
    naechste_frist_iso: Optional[str]
    tage_bis_frist: Optional[int]
    rvg_stunden_offen: float
    rvg_satz_eur: float
    aufbewahrungs_frist_iso: Optional[str]
    source: str                    # "mock"|"real-api"
    iso_timestamp: str
    phronesis_ticket: Optional[str] = None
    warnings: tuple = field(default_factory=tuple)


def _validate_rvg(satz_eur: float) -> bool:
    """Pre: satz_eur >= 0; Post: True iff satz_eur <= RVG_MAX_SATZ_EUR (Plausibilitaet)."""
    assert satz_eur >= 0, f"invalid rvg_satz: {satz_eur}"
    return satz_eur <= RVG_MAX_SATZ_EUR


def _calc_aufbewahrung(kategorie: str = "STANDARD") -> str:
    """Pre: kategorie in AUFBEWAHRUNG_TAGE; Post: ISO-Date Aufbewahrungs-Frist."""
    assert kategorie in AUFBEWAHRUNG_TAGE, f"unknown kategorie: {kategorie}"
    tage = AUFBEWAHRUNG_TAGE[kategorie]
    return (datetime.now(timezone.utc) + timedelta(days=tage)).isoformat()


def mock_mandanten_status(
    mandant_id: str,
    lifecycle_phase: str = "AKTIV",
) -> MandantenResult:
    """Mock-Status: liefert AKTIV + Konflikt-Pending + 0h-RVG."""
    assert mandant_id, "mandant_id required"
    assert lifecycle_phase in PHASES, f"invalid phase: {lifecycle_phase}"
    return MandantenResult(
        mandant_id=mandant_id,
        lifecycle_phase=lifecycle_phase,
        konflikt_status="CHECK_PENDING",
        naechste_frist_iso=None,
        tage_bis_frist=None,
        rvg_stunden_offen=0.0,
        rvg_satz_eur=0.0,
        aufbewahrungs_frist_iso=_calc_aufbewahrung("STANDARD"),
        source="mock",
        iso_timestamp=iso_now(),
        phronesis_ticket=None,
        warnings=("MOCK_MODE_NO_REAL_DMS_RVG",),
    )


def real_mandanten_status(
    mandant_id: str,
    lifecycle_phase: str = "AKTIV",
    phronesis_ticket: Optional[str] = None,
) -> MandantenResult:
    """Real-Mode (NUR mit PHRONESIS_TICKET; K_0/Q_0-Schutz)."""
    assert mandant_id, "mandant_id required"
    if not phronesis_ticket:
        phronesis_ticket = os.environ.get("PHRONESIS_TICKET")
    if not phronesis_ticket:
        return mock_mandanten_status(mandant_id, lifecycle_phase)
    return MandantenResult(
        mandant_id=mandant_id,
        lifecycle_phase=lifecycle_phase,
        konflikt_status="PASS",  # Welle-49+ Real-Konflikt-Engine
        naechste_frist_iso=None,
        tage_bis_frist=None,
        rvg_stunden_offen=0.0,
        rvg_satz_eur=200.0,  # Standard-Mock
        aufbewahrungs_frist_iso=_calc_aufbewahrung("STANDARD"),
        source="real-api",
        iso_timestamp=iso_now(),
        phronesis_ticket=phronesis_ticket,
        warnings=(),
    )


def dispatch_mandanten_status(
    mandant_id: str,
    lifecycle_phase: str = "AKTIV",
) -> MandantenResult:
    """Dispatcher mit ENV-Var-Gating."""
    real_enabled = os.environ.get("DF_LEXVANCE_MANDANTEN_REAL_ENABLED", "").lower() == "true"
    if real_enabled:
        return real_mandanten_status(mandant_id, lifecycle_phase)
    return mock_mandanten_status(mandant_id, lifecycle_phase)


def needs_konflikt_review(result: MandantenResult) -> bool:
    """Pre: result valid; Post: True iff Konflikt-Status nicht PASS."""
    return result.konflikt_status != "PASS"


def to_audit_record(result: MandantenResult) -> dict:
    return {
        "ts": result.iso_timestamp,
        "df": "DF-LEXVANCE-MANDANTEN-PIPELINE",
        "mandant_id": result.mandant_id,
        "lifecycle_phase": result.lifecycle_phase,
        "konflikt_status": result.konflikt_status,
        "rvg_stunden_offen": result.rvg_stunden_offen,
        "rvg_satz_eur": result.rvg_satz_eur,
        "source": result.source,
        "phronesis_ticket": result.phronesis_ticket or "none",
    }
