# src/config/llm_prompts.py
"""
Zentrale, kuratierte LLM-Kontexte & Prompt-Templates für HydroAlert.
Kurz & prägnant halten → stabilere Outputs.
"""

HYDROALERT_CONTEXT_DE = """
# Projekt: HydroAlert – Einsatznahe Niederschlags- & Gefahrenkarten
- Zweck: Verknüpft WMS-Gefahren-/Gefährdungslayer (Hochwasser etc.) mit aktuellen Niederschlagsvorhersagen.
- Zielgruppe: Einsatzkräfte/Kommunen – schnelle Lageeinschätzung: Wann? Wo? Wie stark?
- Architektur (Clean Architecture):
  - config/: zentrale Defaults (Pfade, URLs, Layerlisten, API-Keys)
  - domain/: reine Datenmodelle, keine I/O
  - io/: HTTP/WMS-Requests, Filesystem, DB-Adapter
  - analysis/: Algorithmen ohne Seiteneffekte
  - services/: Orchestrierung (kombiniert io/ + analysis/)
  - use_cases/: CLI/Telegram, Nutzerinteraktion
  - utils/: Logging, Naming, Zeit-Utilities
- Besondere Services:
  - RainGridForecaster: rastert Vorhersage, extrahiert Intensitäten (GRID_SIZE_M, FORECAST_STEP_M)
  - WMS-Downloader: lädt Layer rund um lat/lon (OSM_RADIUS_M, SAMPLE_DISTANCE_M)
  - Evaluation-Service: bewertet/legt Ergebnisse für Location ab
  - Dummy-Data-Service: generiert Testdaten ohne externe Abhängigkeit
- Typische I/O:
  - Eingabe: "lat, lon" (Dezimalgrad), z. B. 49.123, 8.456
  - Ausgabe: Kartenkacheln, CSV/JSON-Cache, Telegram-Hinweise
- Qualitätsprinzipien: PEP8, tiefes Logging, reproduzierbar, keine Hardcoded Paths, .env-basierte Config.

# Dummy-Test auslösen (Telegram/CLI)
- Zweck: Ohne echte Vorhersage/WMS prüfen, ob Pipeline & UI funktionieren.
- Telegram (Beispiel): Befehl /hilfe erklärt es; oder Nachricht "dummy 49.123, 8.456".
- Intern: use_case ruft services.dummy_data_service.generate_dummy_for_location(lat, lon)
- Ergebnis: Generiertes Raster + Kacheln + Evaluation werden wie “echte” Daten weiterverarbeitet/gespeichert.
- Hinweistext: "Dummy-Daten aktiv – Werte sind simuliert."
""".strip()


PROMPT_HINT_COORDS_DE = """\
Du bist kurz, klar, hilfsbereit. Antworte nur auf Deutsch.
Aufgabe: Erkläre in einem Satz, wie man Koordinaten korrekt im Format 'lat, lon' sendet
und gib genau **ein** Beispiel.

Kontext:
{context}
""".strip()


PROMPT_HYDROALERT_EXPLAIN_DE = """\
Du bist der kurze "Überblicks-Assistent" für HydroAlert. Antworte prägnant (max. 120 Wörter), als Stichpunkte.
Inhalt:
- Was HydroAlert macht
- Woraus es besteht (grob)
- Wie man einen Dummy-Test auslöst
- Wie Koordinaten korrekt übermittelt werden

Kontext:
{context}

Nutzerfrage:
{user_text}
""".strip()
