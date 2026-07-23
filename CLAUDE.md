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
