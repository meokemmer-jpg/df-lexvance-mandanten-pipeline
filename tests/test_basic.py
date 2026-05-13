"""Basic Tests fuer DF-LEXVANCE-MANDANTEN-PIPELINE [CRUX-MK]."""
from __future__ import annotations

import os
import sys
import pathlib
import pytest

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.engine import (
    PHASES, RVG_MAX_SATZ_EUR, AUFBEWAHRUNG_TAGE,
    MandantenResult,
    mock_mandanten_status, real_mandanten_status, dispatch_mandanten_status,
    needs_konflikt_review, to_audit_record,
    _validate_rvg, _calc_aufbewahrung,
)


def _clear_env(monkeypatch):
    monkeypatch.delenv("DF_LEXVANCE_MANDANTEN_REAL_ENABLED", raising=False)
    monkeypatch.delenv("PHRONESIS_TICKET", raising=False)


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
    assert result.konflikt_status == "PASS"


def test_env_true_without_phronesis_fallback(monkeypatch):
    """K_0/Q_0-Schutz: ohne PHRONESIS_TICKET → graceful Fallback."""
    _clear_env(monkeypatch)
    monkeypatch.setenv("DF_LEXVANCE_MANDANTEN_REAL_ENABLED", "true")
    result = dispatch_mandanten_status("M-003")
    assert result.source == "mock", "Mandanten-Daten ohne PHRONESIS muss fallback ausloesen"


def test_rvg_satz_validation():
    """RVG-Plausibilitaet: max 350 EUR/h."""
    assert _validate_rvg(100.0)
    assert _validate_rvg(350.0)
    assert not _validate_rvg(351.0)
    assert not _validate_rvg(500.0)


def test_rvg_negative_raises():
    with pytest.raises(AssertionError):
        _validate_rvg(-1.0)


def test_aufbewahrung_kategorien():
    """Conservation: 3 Aufbewahrungs-Kategorien (STANDARD/STRAFRECHT/FAMILIE)."""
    assert "STANDARD" in AUFBEWAHRUNG_TAGE
    assert "STRAFRECHT" in AUFBEWAHRUNG_TAGE
    assert "FAMILIE" in AUFBEWAHRUNG_TAGE
    # STRAFRECHT laengste Frist
    assert AUFBEWAHRUNG_TAGE["STRAFRECHT"] > AUFBEWAHRUNG_TAGE["STANDARD"]


def test_invalid_phase_raises():
    with pytest.raises(AssertionError):
        mock_mandanten_status("M-X", "INVALID_PHASE")


def test_conservation_5_phases():
    """Conservation: alle 5 Lifecycle-Phasen vorhanden."""
    assert len(PHASES) == 5
    expected = {"AKQUISITION", "ONBOARDING", "AKTIV", "ABRECHNUNG", "ABGESCHLOSSEN"}
    assert set(PHASES) == expected


def test_needs_konflikt_review():
    pending = mock_mandanten_status("M-P", "AKQUISITION")
    assert needs_konflikt_review(pending), "CHECK_PENDING muss Review triggern"


def test_audit_record_format():
    result = mock_mandanten_status("M-AUD")
    rec = to_audit_record(result)
    assert {"ts", "df", "mandant_id", "lifecycle_phase", "konflikt_status", "source"} <= set(rec.keys())
    assert rec["df"] == "DF-LEXVANCE-MANDANTEN-PIPELINE"
