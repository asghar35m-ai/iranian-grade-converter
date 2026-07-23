# PaperGeneAI

Lokale, KI-gestützte Analyse wissenschaftlicher Paper (PDF). Ein Paper wird
hochgeladen, der Text lokal extrahiert und durchsucht – Fragen, Zusammen-
fassungen und die Extraktion strukturierter Daten (Gene, Zelltypen,
Signalwege, Methoden …) beantwortet ein lokal laufendes Sprachmodell
(Ollama, `llama3.2`). Es verlassen keine Paper-Inhalte deinen Rechner.

## Starten

Voraussetzung: [Ollama](https://ollama.com) ist installiert und läuft
(`ollama pull llama3.2`, dann z. B. `brew services start ollama`).

```bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

streamlit run LocalBioPaperAI/streamlit_app.py
```

Die App öffnet sich im Browser. Dort ein PDF hochladen und in den Reitern
Fragen stellen, das Paper zusammenfassen lassen oder strukturierte Daten
extrahieren.

## Ordnerstruktur

- `LocalBioPaperAI/streamlit_app.py` – die Weboberfläche (Haupt-Einstiegspunkt)
- `LocalBioPaperAI/src/` – Kernlogik: PDF lesen, Text in Abschnitte teilen,
  Embeddings erzeugen, passende Abschnitte finden, mit dem Sprachmodell
  sprechen, Paper-Kapitel erkennen, strukturierte Daten extrahieren
- `LocalBioPaperAI/data/` – Beispiel-PDF zum Ausprobieren
- `requirements.txt` – benötigte Python-Pakete
