# df-lexvance-mandanten-pipeline [CRUX-MK]

**Welle:** 48 Track-A Wave-1 DC-1
**Status:** SKELETON-CONDITIONAL (NICHT laden vor Martin-Phronesis-Approval Welle-49)
**Coverage:** LexVance Gap-Cluster D (Mandanten-Pipeline)

## Scope

Mandanten-Lifecycle ueber 5 Phasen:
- **AKQUISITION** (Lead-Tracking + Konflikt-Check)
- **ONBOARDING** (Mandat-Vertrag + DSGVO-Einwilligung)
- **AKTIV** (Akten + Fristen + RVG-Zeitabrechnung)
- **ABRECHNUNG** (RVG-Endabrechnung)
- **ABGESCHLOSSEN** (Aufbewahrungs-Frist beginnt)

Output: MandantenResult mit Phase + Konflikt-Status + naechste Frist + RVG-Stunden + Aufbewahrungs-Frist.

## LexVance-Coverage-Mapping

| LexVance-Funktion | Vor Welle-48 | Nach Welle-48 |
|-------------------|---------------|----------------|
| Mandanten-Akquisition + Lead-Tracking | UNGEDECKT | df-lexvance-mandanten-pipeline |
| Konflikt-Check (Cross-Mandanten) | UNGEDECKT | df-lexvance-mandanten-pipeline |
| Akten-Verwaltung + DMS | UNGEDECKT | df-lexvance-mandanten-pipeline |
| Fristen-Tracker (Klage/Einspruch/Verjaehrung) | UNGEDECKT | df-lexvance-mandanten-pipeline |
| RVG-Stundenabrechnung | UNGEDECKT | df-lexvance-mandanten-pipeline |
| Aufbewahrungs-Frist (§ 50 BORA) | UNGEDECKT | df-lexvance-mandanten-pipeline |

## Compliance

- K11-K16 voll mit **K11 verstaerkt** (Cross-Mandanten-Read VERBOTEN, Konflikt-Risiko)
- LC1-LC5 voll mit eigener DLQ pro Mandant
- Trinity-Pattern (Conservative/Aggressive/Contrarian via Konflikt-Status)
- Audit-Trail mit Privileged-Communication-Schutz
- ENV-Var-gated Default-Disabled
- **PHRONESIS_TICKET Pflicht** (Mandanten-Daten = K_0/Q_0)
- RVG-Plausibilitaets-Check (max 350 EUR/h)

## Activation

1. Martin-Phronesis-Approval (Welle-49 Pflicht, **K_0/Q_0 Mandanten-Daten**)
2. Cross-LLM-3OF3-Audit (Codex+Gemini+Copilot)
3. Tests passing: `python3 -m pytest tests/ -v`
4. Real-Mode: ENV `DF_LEXVANCE_MANDANTEN_REAL_ENABLED=true` + `PHRONESIS_TICKET=PT-...`
5. DMS-Integration + RVG-Corpus-Connector (Welle-49 Pflicht)

## STOP

`touch /tmp/df-lexvance-mandanten-pipeline.stop` oder LaunchAgent unloaden.

## Welle-49+ Roadmap

- [ ] Konflikt-Check-Engine (Cross-Mandanten ohne Cross-Read-Verletzung) (Welle-49)
- [ ] DMS-Integration (Akten-Versionierung) (Welle-49)
- [ ] Fristen-Tracker (Klage/Einspruch/Revision/Verjaehrung) (Welle-49)
- [ ] RVG-Stundenabrechnung-Engine (Welle-50)
- [ ] Privileged-Communication-Audit-Schutz (Welle-50)
- [ ] Mandanten-CRM-UI (Welle-51+)
- [ ] Cross-LLM-3OF3-Audit-Verdict (Welle-49)

## rho

~150k EUR/J (Verjaehrungs-Vermeidung + RVG-Praezision + Konflikt-Vermeidung).

[CRUX-MK]
