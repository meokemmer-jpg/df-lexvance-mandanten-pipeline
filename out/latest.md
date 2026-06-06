# df-lexvance-mandanten-pipeline — Output [CRUX-MK]
*Autonom aktiviert 2026-06-05T10:44:59.108318+00:00 | ollama-local/qwen2.5:14b-instruct*

## MandantenLifecycle-Pipeline Dokumentation

### Übersicht:
Die Dark-Factory 'df-lexvance-mandanten-pipeline' ist eine strukturierte Sy
Systemarchitektur zur Unterstützung des Mandatentreibens innerhalb der LexV
LexVance Anwaltskanzlei. Diese Factory umfasst fünf Phasen, die den gesamte
gesamten Lebenszyklus eines Mandanten abdecken: Akquisition, Onboarding, Ak
Aktivphase, Abrechnung und Schließungsphase.

### 1. Phase - AKQUISITION:
Die Akquise-Phase beinhaltet das Tracking von Leads und einen ausgiebigen K
Konflikt-Check, um sicherzustellen, dass der potenzielle Mandant mit besteh
bestehenden Fällen in Einklang steht.

### 2. Phase - ONBOARDING:
Im Onboarding-Prozess wird der Vertrag des Mandanten aufgesetzt und eine DS
DSGVO-Einwilligung abgefragt. Dies stellt sicher, dass alle rechtlichen Vor
Voraussetzungen erfüllt sind.

### 3. Phase - AKTIV:
In dieser Phase wird die Aktenverwaltung durchgeführt, Fristen geprüft und 
RVG-Zeitabrechnung durchgeführt. Dies ermöglicht es der Kanzlei, alle relev
relevanten Dokumente zu verwalten und rechtzeitige Maßnahmen vorzubereiten.
vorzubereiten.

### 4. Phase - ABRECHNUNG:
Die Abrechnungsphase umfasst die RVG-Endabrechnung für den Mandanten, was d
den Abschluss des gesamten Prozesses darstellt.

### 5. Phase - ABGESCHLOSSEN:
Nach dem Abschluss der Rechtssache beginnt die Aufbewahrungsfrist gemäß § 5
50 BORA (Berufshaftpflichtversicherungsgesetz).

### Ausgabe des Systems:
Das System produziert ein MandantenResult-Objekt, das Informationen zu den 
einzelnen Phasen enthält, einschließlich Konfliktstatus, der nächsten Frist
Frist, RVG-Stunden und der Aufbewahrungsfrist.

### Compliance-Anforderungen:
Die Factory muss K11-Konformität (verstärkt für Cross-Mandanten-Read Verbot
Verbot), LC1-LC5-Datensicherheit und das Trinity-Pattern für Konfliktstatus
Konfliktstatus-Ermittlung erfüllen. Ein Audit-Trail ist notwendig, um privi
privilegierte Kommunikation zu schützen. Die Factory ist durch Umgebungsvar
Umgebungsvariablen eingeschränkt und kann nur aktiviert werden, wenn ein sp
spezifisches PHRONESIS-Ticket vorliegt.

### Aktivierung:
1. Martin-Phronesis-Zustimmung (Welle 49)
2. Cross-LLM-3OF3-Audit
3. Bestandene Tests (`python3 -m pytest tests/ -v`)
4. Real-Modus aktivieren mit spezifischen Umgebungsvariablen und Ticket

### Roadmap:
Für die Zukunft sind Pläne zur Verbesserung der Konflikt-Check-Engine, Inte
Integration einer DMS (Document Management System), Implementierung eines F
Fristentrackers, Entwicklung einer RVG-Stundenabrechnungsengine und Einführ
Einführung eines Mandanten-CRM-UI geplant.

Diese Dokumentation stellt die grundlegende Struktur und Funktionalität der
der df-lexvance-mandanten-pipeline dar.