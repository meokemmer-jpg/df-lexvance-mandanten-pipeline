"""Basic Tests fuer DF-LEXVANCE-MANDANTEN-PIPELINE [CRUX-MK]."""
from __future__ import annotations

import json
import pathlib
import sys
from datetime import datetime, timezone

import pytest

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.engine import (
    AUFBEWAHRUNG_TAGE,
    PHASES,
    RVG_MAX_SATZ_EUR,
    dispatch_mandanten_status,
    mock_mandanten_status,
    needs_konflikt_review,
    real_mandanten_status,
    run_mandanten_pipeline,
    to_audit_record,
    _calc_aufbewahrung,
    _validate_rvg,
)


def _clear_env(monkeypatch):
    monkeypatch.delenv("DF_LEXVANCE_MANDANTEN_REAL_ENABLED", raising=False)
    monkeypatch.delenv("DF_LEXVANCE_MANDANTEN_PAYLOAD", raising=False)
    monkeypatch.delenv("PHRONESIS_TICKET", raising=False)


def _write_payload(path: pathlib.Path, payload: dict) -> pathlib.Path:
    path.write_text(json.dumps(payload, sort_keys=True), encoding="utf-8")
    return path


def test_pipeline_discriminates_adversarial_conflict_from_clean_case(tmp_path):
    now = datetime(2026, 5, 17, tzinfo=timezone.utc)
    clean_payload = {
        "mandant_id": "M-CLEAN",
        "lifecycle_phase": "AKQUISITION",
        "conflict_parties": ["Alpha GmbH"],
        "known_adverse_parties": ["Beta AG"],
        "deadline_iso": "2026-05-27T00:00:00+00:00",
        "billable_minutes": 120,
        "paid_minutes": 60,
        "rvg_satz_eur": 200.0,
        "kategorie": "STANDARD",
    }
    adversarial_payload = {
        **clean_payload,
        "mandant_id": "M-ADVERSARIAL",
        "conflict_parties": ["Alpha GmbH", "Omega SE"],
        "known_adverse_parties": ["  omega se  "],
        "billable_minutes": 240,
        "paid_minutes": 0,
    }

    clean_file = _write_payload(tmp_path / "clean_case.json", clean_payload)
    adversarial_file = _write_payload(tmp_path / "adversarial_case.json", adversarial_payload)

    clean = run_mandanten_pipeline(clean_file, now=now)
    adversarial = run_mandanten_pipeline(adversarial_file, now=now)

    assert clean.payload_hash != adversarial.payload_hash
    assert clean.konflikt_status == "PASS"
    assert adversarial.konflikt_status == "FAIL"
    assert not needs_konflikt_review(clean)
    assert needs_konflikt_review(adversarial)
    assert clean.rvg_stunden_offen != adversarial.rvg_stunden_offen
    assert "KONFLIKT_TREFFER" not in clean.warnings
    assert "KONFLIKT_TREFFER" in adversarial.warnings


def test_default_mock_no_env(monkeypatch):
    _clear_env(monkeypatch)
    result = dispatch_mandanten_status("M-001")
    assert result.source == "mock"
    assert result.lifecycle_phase == "AKTIV"
    assert result.konflikt_status == "CHECK_PENDING"
    assert result.phronesis_ticket is None


def test_env_true_with_phronesis(monkeypatch):
    _clear_env(monkeypatch)
    monkeypatch.setenv("DF_LEXVANCE_MANDANTEN_REAL_ENABLED", "true")
    monkeypatch.setenv("PHRONESIS_TICKET", "PT-W48-MANDANT-001")
    result = dispatch_mandanten_status("M-002")
    assert result.source == "real-api"
    assert result.konflikt_status == "CHECK_PENDING"


def test_env_true_without_phronesis_fallback(monkeypatch):
    _clear_env(monkeypatch)
    monkeypatch.setenv("DF_LEXVANCE_MANDANTEN_REAL_ENABLED", "true")
    result = dispatch_mandanten_status("M-003")
    assert result.source == "mock", "Mandanten-Daten ohne PHRONESIS muss fallback ausloesen"


def test_real_mode_reads_file_payload_when_authorized(monkeypatch, tmp_path):
    _clear_env(monkeypatch)
    payload_file = _write_payload(
        tmp_path / "real_payload.json",
        {
            "mandant_id": "M-FILE",
            "lifecycle_phase": "AKTIV",
            "conflict_parties": ["Kanzlei Bestand"],
            "known_adverse_parties": ["Kanzlei Bestand"],
            "billable_minutes": 90,
            "paid_minutes": 30,
            "rvg_satz_eur": 250.0,
            "kategorie": "FAMILIE",
        },
    )
    monkeypatch.setenv("PHRONESIS_TICKET", "PT-FILE")
    monkeypatch.setenv("DF_LEXVANCE_MANDANTEN_PAYLOAD", str(payload_file))

    result = real_mandanten_status("IGNORED-BECAUSE-FILE-WINS")

    assert result.source == "real-file"
    assert result.mandant_id == "M-FILE"
    assert result.konflikt_status == "FAIL"
    assert result.rvg_stunden_offen == 1.0


def test_rvg_satz_validation():
    assert _validate_rvg(100.0)
    assert _validate_rvg(350.0)
    assert not _validate_rvg(351.0)
    assert not _validate_rvg(500.0)


def test_rvg_negative_raises():
    with pytest.raises(AssertionError):
        _validate_rvg(-1.0)


def test_aufbewahrung_kategorien():
    assert "STANDARD" in AUFBEWAHRUNG_TAGE
    assert "STRAFRECHT" in AUFBEWAHRUNG_TAGE
    assert "FAMILIE" in AUFBEWAHRUNG_TAGE
    assert AUFBEWAHRUNG_TAGE["STRAFRECHT"] > AUFBEWAHRUNG_TAGE["STANDARD"]
    assert _calc_aufbewahrung("STANDARD")


def test_invalid_phase_raises():
    with pytest.raises(AssertionError):
        mock_mandanten_status("M-X", "INVALID_PHASE")


def test_conservation_5_phases():
    assert len(PHASES) == 5
    expected = {"AKQUISITION", "ONBOARDING", "AKTIV", "ABRECHNUNG", "ABGESCHLOSSEN"}
    assert set(PHASES) == expected


def test_needs_konflikt_review():
    pending = mock_mandanten_status("M-P", "AKQUISITION")
    assert needs_konflikt_review(pending), "CHECK_PENDING muss Review triggern"


def test_audit_record_format():
    result = mock_mandanten_status("M-AUD")
    rec = to_audit_record(result)
    assert {"ts", "df", "mandant_id", "lifecycle_phase", "konflikt_status", "source", "payload_hash"} <= set(rec.keys())
    assert rec["df"] == "DF-LEXVANCE-MANDANTEN-PIPELINE"
