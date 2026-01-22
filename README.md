# CouchDB-Importer

Ein vielseitiges Python-Skript für den einfachen Import von CSV- und JSON-Daten in eine CouchDB.

## Features

*   **CSV-Support**: Mit Spaltenvalidierung und Fortschrittsanzeige.
*   **JSON-Support**: Unterstützt verschiedene Strukturen (CouchDB-Standard `{"docs": [...]}` oder einfache Listen).
*   **Fehlertoleranz**: Automatisches Verpacken von einfachen Datentypen (Strings/Zahlen) in Objekte.
*   **Auto-DB-Erstellung**: Erstellt die Zieldatenbank automatisch, falls sie noch nicht existiert. 🚀

## Installation

```bash
git clone https://github.com/wanjus/couchdb-importer.git
cd couchdb-importer
pip install -r requirements.txt
```

## Nutzung

Das Skript wird über die Kommandozeile gesteuert:

```bash
python CouchDB‑Importer.py --file <DATEIPFAD> --db <DATENBANKNAME> [OPTIONEN]
```

### Parameter:
*   `--file`: Pfad zur Quelldatei (`.csv` oder `.json`). **(Erforderlich)**
*   `--db`: Name der Ziel-Datenbank. **(Erforderlich)**
*   `--url`: CouchDB-URL (Standard: `http://localhost:5984`).
*   `--user`: CouchDB-Benutzername.
*   `--password`: CouchDB-Passwort.
*   `--id-column`: Spalte oder Feldname, der als Dokument-ID (`_id`) verwendet werden soll.

## Beispiele

### Import einer JSON-Datei:
```bash
python CouchDB‑Importer.py --file test.json --db test --user admin --password admin
```

### Import einer CSV-Datei:
```bash
python CouchDB‑Importer.py --file test.csv --db test --user admin --password admin
```

### Mit spezifischer ID-Spalte:
```bash
python CouchDB‑Importer.py --file daten.csv --db meine_db --id-column kunden_nr
```
