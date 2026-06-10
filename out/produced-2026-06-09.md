# df-lexvance-mandanten-pipeline — PRODUKTION [CRUX-MK]
*2026-06-09T15:18:03.245741+00:00 | ollama-local/kemmer-14b-ctx8k*

# Dokumentation der Dark-Factory 'df-lexvance-mandanten-pipeline'

## Übersicht

Die Dark-Factory 'df-lexvance-mandanten-pipeline' ist eine strukturierte Systemarchitektur, die den gesamten Lebenszyklus von Mandatengeschäften innerhalb der LexVance Anwaltskanzlei abdeckt. Sie umfasst fünf Phasen: Akquisition, Onboarding, Aktivphase, Abrechnung und Abschlussphase. Diese Factory wurde entwickelt, um den Mandanten-Lifecycle zu optimieren und gleichzeitig Compliance-Standards einzuhalten.

## Mandanten-Lifecycle Phasen

### 1. Phase - AKQUISITION
Die Akquise-Phase beginnt mit der Identifikation potentieller Mandanten (Leads). Der Prozess beinhaltet eine detaillierte Analyse und Bewertung dieser Leads, um zu bestimmen, ob sie für die Kanzlei interessant sind. Ein wesentlicher Bestandteil ist der Konflikt-Check, der sicherstellt, dass kein Interessenkonflikt zwischen dem potenziellen Mandanten und bestehenden Mandanten existiert.

### 2. Phase - ONBOARDING
Nach erfolgreicher Akquise beginnt die Onboarding-Phase. Hier wird der Mandatvertrag ausgehandelt und abgeschlossen. Zusätzlich muss eine DSGVO-Einwilligung von den Mandanten erlangt werden, um alle rechtlichen Voraussetzungen für die Bearbeitung des Falles zu erfüllen.

### 3. Phase - AKTIV
In dieser Phase wird die tatsächliche Arbeit am Fall durchgeführt. Dies beinhaltet die Verwaltung von Akten und Dokumenten im DMS (Document Management System), den regelmäßigen Überprüfung der Rechtlichkeiten wie Klagefristen, Einspruchsmöglichkeiten oder Revisionstermine sowie die RVG-Zeitabrechnung für geleistete Arbeit.

### 4. Phase - ABRECHNUNG
Die Abrechnungsphase ist das Ende des Mandanten-Lifecycles und beginnt mit der Durchführung einer RVG-Endabrechnung, welche eine detaillierte Auflistung aller geleisteten Leistungen für den Mandanten enthält.

### 5. Phase - ABGESCHLOSSEN
Nachdem alle formalen Abnahmeverfahren abgeschlossen sind, beginnt die Aufbewahrungsfrist gemäß § 50 BORA (Berufshaftpflichtversicherungsgesetz). Diese Phase ist für die Dokumentation und Datenspeicherung kritisch.

## Ausgabe des Systems

Das System erzeugt ein MandantenResult-Objekt, das umfassende Informationen über den gesamten Lebenszyklus eines Mandanten enthält. Dieses Objekt umfasst:
- Die aktuelle Phase im Lebenszyklus.
- Der Status von Konflikten oder Interessenkollisionen.
- Eine Aufstellung der nächsten nötigen Fristen (z.B. Klagefristen, Einspruchstermine).
- RVG-Stunden zur Berechnung der Rechnungen an Mandanten.
- Die beginnende Aufbewahrungsfrist für Dokumente gemäß § 50 BORA.

## Compliance-Anforderungen

### K11-Konformität (verstärkt)
Die Factory muss die K11-Konformität einhalten, was bedeutet, dass es eine Verbot gibt, Cross-Mandanten-Reads durchzuführen. Dies ist entscheidend für das Schutz der Privatsphäre und Rechtlichen Vorschriften.

### Datensicherheit (LC1-LC5)
Es muss LC1-LC5-Datensicherheitsrichtlinien eingehalten werden, um die Integrität der Mandanten-Daten sicherzustellen. Dies beinhaltet eine spezielle Datenlagerungslösung für jedes Mandantenkonto.

### Trinity-Pattern
Die Factory muss das Trinity-Pattern implementieren, welches ein Muster bietet, um unterschiedliche Perspektiven (Konservativ, Aggressiv und Konträr) zu einem bestimmten Konfliktsstatus einzubinden. Dies unterstützt in der Entscheidungsfindung.

### Audit-Trail
Ein vollständiger Audit-Trail ist notwendig, um jegliche privilegierte Kommunikation während des gesamten Lebenszyklus von Mandanten zu dokumentieren und schützen.

## Aktivierung der Factory

Die 'df-lexvance-mandanten-pipeline' kann nur aktiviert werden nachdem bestimmte Voraussetzungen erfüllt wurden:
1. Zustimmung durch Martin-Phronesis (Welle 49).
2. Bestehen eines Cross-LLM-Audits, bestehend aus drei Teilprüfungen durch Codex, Gemini und Copilot.
3. Erfolgreiche Durchführung aller Tests (`python3 -m pytest tests/ -v`).
4. Aktivierung im Realmodus mit spezifischen Umgebungsvariablen `DF_LEXVANCE_MANDANTEN_REAL_ENABLED=true` sowie einem speziellen PHRONESIS-Ticket `PHRONESIS_TICKET=PT-...`.

## Roadmap für zukünftige Entwicklungen

Für die Zukunft sind folgende Verbesserungsschritte geplant:
- Entwicklung einer Engine zur Durchführung von Konfliktprüfung (Welle 49).
- Implementierung der DMS-Integration, einschließlich Versionskontrolle von Dokumenten (Welle 49).
- Erweiterung um einen Fristentracker für Klagen, Einspruch oder Revisionsmöglichkeiten (Welle 49).
- Entwicklung einer Engine zur RVG-Stundenabrechnung (Welle 50).
- Implementierung des Audit-Schutzes für privilegierte Kommunikation (Welle 50).
- Erstellung eines Mandanten-CRM-UI, um eine effiziente Interaktion mit Mandantendaten zu ermöglichen (Welle 51+).

Diese Factory ist ein bedeutender Schritt in Richtung einer vollautomatisierten und datengetriebenen Methode zur Verwaltung von Mandatengeschäften bei LexVance.