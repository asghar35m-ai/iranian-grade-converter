# PaperGeneAI

## Über den Nutzer

Der Projektinhaber ist Biologe, kein Informatiker. Deshalb gilt:

- Erkläre auf **Deutsch** und in einfachen Worten, was du tust und warum.
- Arbeite in **kleinen, nachvollziehbaren Schritten**. Nie zehn Dateien auf einmal.
- Nutze standardmäßig den **Plan mode**: erst beschreiben, dann nach Freigabe umsetzen.
- Wenn eine Entscheidung fachlich (biologisch) ist, frag nach. Wenn sie technisch ist, entscheide selbst und begründe kurz.
- Keine ungefragten großen Refactorings.

## Ziel des Projekts

Ein Werkzeug, das wissenschaftliche Publikationen zur Stammzell-Differenzierung
auswertet und daraus ableitet, welche Gene, Proteine und Signalwege für einen
gegebenen Differenzierungspfad (Ausgangszelltyp → Zielzelltyp) am wichtigsten sind.

Drei Anwendungsfälle, die auf **denselben Daten** aufsetzen:

1. **Literatur durchsuchbar machen** — semantische Suche über Volltexte
2. **Protokolle vergleichen** — welche Faktoren, Konzentrationen, Zeitfenster, welche Effizienz
3. **Gene und Proteine priorisieren** — nachvollziehbar begründetes Ranking

## Pilotpfad

Der erste Differenzierungspfad, an dem Schema, Ingestion und Scoring
entwickelt und getestet werden: **iPSC → pankreatische Betazellen**.

**Prüfgene:** PDX1, NKX6-1, NEUROG3, MAFA. Diese vier sind in der Literatur
zu diesem Pfad gut etabliert. Landet keines davon im Scoring weit oben,
stimmt etwas mit Extraktion, Normalisierung oder Scoring nicht — das ist
der Sanity-Check für jede Phase.

## Zielarchitektur

Fünf Verarbeitungsstufen, eine gemeinsame Datenbank:

1. **Ingestion** — Europe PMC, PubMed (E-utilities), bioRxiv, GROBID für eigene PDFs
2. **Normalisierung** — PubTator3 für Entitäten, mygene.info für Gen-IDs, Cell Ontology für Zelltypen
3. **Extraktion** — LLM wandelt Methods-Abschnitte in striktes JSON (Protokoll-Datensätze)
4. **Anreicherung** — UniProt, STRING, Reactome, DoRothEA, CellMarker
5. **Scoring und API** — Ranking, FastAPI als Backend, Streamlit nur noch als Oberfläche

### Dienste (Docker Compose)

| Dienst | Zweck |
|---|---|
| `postgres` mit pgvector | relationale Daten und Embeddings in einer DB |
| `redis` | Job-Queue |
| `api` | FastAPI + RQ-Worker, alles Rechenintensive |
| `ui` | Streamlit, spricht nur per HTTP mit `api` |

**Zentrale Regel:** In Streamlit steht keine Pipeline-Logik. Streamlit holt JSON
und stellt es dar. Grund: Streamlit führt bei jeder Interaktion das komplette
Skript neu aus — solange dort Logik drinsteckt, wird die App nie schnell.

### Verzeichnisstruktur (Zielzustand)

```
stemdiff/
├─ docker-compose.yml
├─ core/          models.py, config.py, db.py
├─ ingest/        europepmc.py, pubmed.py, biorxiv.py, grobid.py
├─ normalize/     pubtator.py, gene_ids.py, celltypes.py
├─ extract/       schema.py, llm.py
├─ enrich/        uniprot.py, string.py, reactome.py, dorothea.py
├─ score/         components.py, combine.py
├─ api/           main.py
├─ worker/        tasks.py
└─ ui/            app.py
```

Jeder externe Client kennt nur seine API und gibt Pydantic-Objekte zurück —
kein DB-Zugriff, kein eigenes Caching. Caching (`requests-cache`, SQLite-Backend)
und Rate-Limiting sitzen zentral in `core/config.py`.

## Datenmodell — die zwei wichtigen Entscheidungen

**1. Entitäten und Erwähnungen trennen.**

```
entity(id, type, canonical_id, symbol, name)      -- Entrez 6657, UniProt P48431, CL:0000034
mention(doc_id, section_id, entity_id, span, source, confidence)
```

Gennamen niemals als reine Strings speichern. Sonst sind SOX2, Sox2 und
"SRY-box 2" drei verschiedene Gene und jedes Ranking ist wertlos.

**2. Score-Komponenten einzeln speichern, nicht den Endwert.**

```
gene_score(entity_id, target_celltype_id, component, value, computed_at)
```

Komponenten: `literature`, `regulon`, `centrality`, `expression`, `perturbation`.
Die Gewichtung passiert erst bei der Abfrage. So kann der Nutzer die Gewichte
im UI verstellen und sieht das Ergebnis sofort, ohne Neuberechnung.

Weitere Tabellen: `documents`, `chunks` (mit Embedding), `sections`,
`protocols` → `protocol_steps` → `protocol_factors`, `protocol_markers`,
`job_runs`.

## Job-Pipeline

Jede Stufe ist ein eigener, **idempotenter** Job mit Statuseintrag pro Dokument
in `job_runs`. Damit kann die Extraktion mit verbessertem Prompt neu über tausende
Paper laufen, ohne alles neu herunterzuladen — und ein Absturz bei Paper 3000
kostet nichts.

## Externe APIs — Regeln

- **Immer cachen.** Jede Antwort in den lokalen Cache, bevor sie verarbeitet wird.
- **Rate-Limits einhalten:** NCBI 3 Anfragen/s ohne API-Key, 10/s mit Key.
  Bei anderen Diensten defensiv bleiben.
- **Nie im UI-Thread aufrufen.** Externe Aufrufe laufen ausschließlich im Worker.
- API-Keys kommen aus `.env`, niemals in den Code, `.env` steht in `.gitignore`.

## Provenienz — nicht verhandelbar

Jede Aussage im Ergebnis muss auf eine PMID und eine Textstelle zurückführbar
sein. Ein Ranking ohne Beleg ist für die Laborarbeit unbrauchbar. Wenn das LLM
etwas extrahiert, wird die Quellstelle mitgespeichert.

## Roadmap

- [ ] **Phase 0** — Aufräumen: Doppelte Streamlit-Apps zusammenführen,
      projektfremde Dateien (z. B. `notenrechner.py`) entfernen, `.env`-Handling,
      `requirements.txt` sauber
- [ ] **Phase 1** — Schema, Ingestion, Caching. Ziel: 500 Paper zu einem
      Differenzierungspfad reproduzierbar in der DB
- [ ] **Phase 2** — Normalisierung via PubTator3
- [ ] **Phase 3** — Hybride Suche (Postgres-Volltext + pgvector, fusioniert per
      Reciprocal Rank Fusion)
- [ ] **Phase 4** — LLM-Protokollextraktion
- [ ] **Phase 5** — Anreicherung und Scoring

Erst wenn eine Phase läuft und getestet ist, beginnt die nächste.

## Was du nicht tun sollst

- Keine Bibliothek einführen, die nicht in `requirements.txt` steht, ohne zu fragen
- Keine Datenbank-Migration ohne Backup-Hinweis
- Kein Gen-Ranking ausliefern, das nicht auf Quellen zurückführbar ist
- Keine Platzhalter- oder Fantasiedaten in der Oberfläche anzeigen

# Ideen für später

Diese Features steckten in der alten `app.py` (Wurzel-Verzeichnis), die beim
Phase-0-Aufräumen gelöscht wurde, weil `LocalBioPaperAI/streamlit_app.py`
fachlich die überlegene App ist. Reiner Bedienkomfort ging dabei verloren
und könnte bei Bedarf in `streamlit_app.py` nachgebaut werden:

- **Chatverlauf**: Fragen und Antworten der Sitzung wurden als fortlaufender
  Chat gespeichert und angezeigt (`st.session_state.chat_history`,
  `st.chat_input`), statt nur die letzte Frage/Antwort zu zeigen.
- **Seitenleiste (Sidebar)**: PDF-Upload, Anzahl-Slider und Quellen-Checkbox
  waren in einer Sidebar gebündelt, inklusive eines eigenen
  "🗑️ Chatverlauf löschen"-Buttons.
- **Anleitungstext**: Beim Start ohne hochgeladenes PDF erschien eine
  ausklappbare Kurzanleitung ("So funktioniert die App", 6 Schritte).
- **Quellen-Checkbox**: Ein Kontrollkästchen, mit dem sich die Anzeige der
  verwendeten Paper-Abschnitte ein-/ausschalten ließ.

Den alten Code findet man im Commit `9332978` ("Add PaperGeneAI app before
Phase-0 cleanup") unter `app.py`.
