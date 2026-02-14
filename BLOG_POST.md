# 🚀 Nie wieder Stress beim CouchDB-Import: CSV & JSON in Sekunden laden

*"Nur mal kurz ein paar Testdaten importieren..."* – jeder Entwickler kennt diesen Satz. Und jeder weiß, dass daraus oft eine Stunde Frust wird: Kaputte JSON-Formate, Encoding-Fehler in CSVs oder endlose `curl`-Befehle, die man sich nie merken kann.

Wir – das **Team Wanju & KI Gemini** – hatten genug davon. Deshalb haben wir ein Tool gebaut, das einfach funktioniert.

## Das Problem

CouchDB ist großartig, aber Daten hineinzubekommen, kann nervig sein.
*   **Fauxton** (das Web-UI) ist okay für einzelne Dokumente, aber mühsam für Massen-Uploads.
*   **Curl** ist mächtig, aber wehe, du vergisst ein Anführungszeichen unter Windows.
*   **Eigene Skripte** schreibt man jedes Mal neu, und sie brechen beim ersten Sonderzeichen.

## Die Lösung: CouchDB-Importer

Unser [CouchDB-Importer](https://github.com/wanjus/couchdb-importer) ist ein "Schweizer Taschenmesser" für den Datenimport, geschrieben in Python. Es ist pragmatisch, robust und Open Source.

### Was kann es?

1.  **CSV, JSON & PDF Support:** Egal ob Excel-Export, API-Dump oder Dokumenten-Archiv, das Tool frisst jetzt alles.
2.  **PDF-Intelligenz:** PDFs werden nicht nur als Binärdatei angehängt, sondern das Skript versucht auch, den Text zu extrahieren, damit er in CouchDB durchsuchbar ist.
3.  **JSON & JSONL:** Neben Standard-JSON-Listen wird nun auch das populäre JSON-Lines-Format (`.jsonl`) unterstützt.
4.  **Auto-DB:** Wenn die Zieldatenbank nicht existiert, wird sie einfach erstellt. Kein manuelles `PUT` mehr nötig.
5.  **Robustheit:** Timeouts verhindern, dass das Skript bei Netzwerkproblemen hängen bleibt. Einfache Werte werden automatisch in Objekte verpackt.
6.  **Feedback:** Eine Fortschrittsanzeige hält dich auf dem Laufenden.

## Schnellstart

Du brauchst nur Python.

```bash
# 1. Repo klonen
git clone https://github.com/wanjus/couchdb-importer.git
cd couchdb-importer

# 2. Abhängigkeiten installieren
pip install -r requirements.txt

# 3. Daten importieren (Beispiel)
python CouchDB-Importer.py --file meine_daten.csv --db testdb --user admin --password secret
```

Das war's. Deine Daten sind drin.

## Mach mit!

Das Projekt ist **Open Source (MIT Lizenz)**. Wir freuen uns über Sterne auf GitHub, Issues oder Pull Requests.

👉 **[Zum GitHub Repository](https://github.com/wanjus/couchdb-importer)**

---
*Entwickelt mit ❤️ und Python von Jürgen (Wanju) und Gemini.*
