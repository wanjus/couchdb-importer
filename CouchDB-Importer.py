#!/usr/bin/env python3
"""
 * author: Team Wanju & KI Gemini
 * created: 22-01-2026
 * copyright: 2026
"""

import csv
import json
import argparse
import requests
import base64
import mimetypes
from pathlib import Path

try:
    import PyPDF2
except ImportError:
    PyPDF2 = None

# ---------------------------------------------------------
# Hilfsfunktion: Prüfen, ob DB existiert – sonst erstellen
# ---------------------------------------------------------
def ensure_database(db_url, db_name, auth=None):
    url = f"{db_url}/{db_name}"
    try:
        r = requests.get(url, auth=auth, timeout=10)
    except requests.exceptions.RequestException as e:
        print(f"✖ Verbindungsfehler zu CouchDB ({url}): {e}")
        return False

    if r.status_code == 200:
        print(f"✔ Datenbank '{db_name}' existiert bereits.")
        return True

    if r.status_code == 404:
        print(f"⚠ Datenbank '{db_name}' existiert nicht – wird erstellt...")
        r = requests.put(url, auth=auth, timeout=10)
        if r.status_code in (200, 201):
            print(f"✔ Datenbank '{db_name}' wurde erstellt.")
            return True
        else:
            print(f"✖ Fehler beim Erstellen der DB: {r.text}")
            return False

    print(f"✖ Unerwartete Antwort beim DB-Check: {r.text}")
    return False


# ---------------------------------------------------------
# Logik: CSV einlesen
# ---------------------------------------------------------
def read_csv_data(file_path, id_column=None):
    print(f"ℹ Lese CSV-Datei: {file_path}")
    
    rows = []
    with open(file_path, newline='', encoding='utf-8') as f:
        # Erstes Einlesen für Spalten-Validierung und Zeilen-Zählung
        reader = csv.DictReader(f)
        columns = reader.fieldnames
        if id_column and id_column not in columns:
            raise ValueError(f"Die ID-Spalte '{id_column}' existiert nicht in der CSV ({columns}).")
        
        # Zeilen zählen (wir sind bereits nach dem Header)
        # Wir sammeln die Zeilen direkt, um nicht doppelt zu lesen
        for i, row in enumerate(reader, start=1):
            # ID setzen
            doc_id = row[id_column] if id_column else str(i)
            # Falls noch keine _id da ist, setzen
            if "_id" not in row:
                row["_id"] = doc_id
            
            rows.append(row)
            # Fortschrittsanzeige (wir kennen das Total noch nicht genau ohne Vorab-Scan, 
            # aber wir können es einfach hochzählen)
            print(f"→ Verarbeite Zeile {i}", end="\r")
    
    print(f"\n✔ CSV vollständig eingelesen ({len(rows)} Dokumente).")
    return rows


# ---------------------------------------------------------
# Logik: JSON einlesen
# ---------------------------------------------------------
def read_json_data(file_path, id_column=None):
    print(f"ℹ Lese JSON-Datei: {file_path}")
    
    rows = []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            # Versuch 1: Standard JSON (Liste oder Objekt)
            try:
                data = json.load(f)
                if isinstance(data, dict) and "docs" in data:
                    print("ℹ Erkanntes Format: {'docs': [...]}")
                    rows = data["docs"]
                elif isinstance(data, list):
                    print("ℹ Erkanntes Format: Liste [...]")
                    rows = data
                elif isinstance(data, dict):
                    print("ℹ Erkanntes Format: Einzelnes Objekt {...}")
                    rows = [data]
            except json.JSONDecodeError:
                # Versuch 2: JSON Lines (JSONL)
                f.seek(0)
                print("ℹ Versuche Format: JSON Lines (JSONL)...")
                for line_num, line in enumerate(f, start=1):
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        rows.append(json.loads(line))
                    except json.JSONDecodeError as e:
                        print(f"⚠ Fehler in Zeile {line_num}: {e}")
                
                if rows:
                    print(f"✔ Erkanntes Format: JSONL ({len(rows)} Dokumente)")
                else:
                    raise ValueError("Unbekanntes JSON-Format oder ungültiges JSON.")

    except Exception as e:
        raise ValueError(f"Fehler beim Verarbeiten der JSON-Datei: {e}")

    # Smart Wrap & IDs
    cleaned_rows = []
    for i, item in enumerate(rows):
        doc = item
        if not isinstance(item, dict):
            doc = {"value": item}
        
        if id_column and id_column in doc:
            doc["_id"] = str(doc[id_column])
        
        cleaned_rows.append(doc)

    print(f"✔ {len(cleaned_rows)} Dokumente aus JSON geladen.")
    return cleaned_rows


# ---------------------------------------------------------
# Logik: PDF einlesen (Text extrahieren + Attachment)
# ---------------------------------------------------------
def read_pdf_data(file_path):
    print(f"ℹ Lese PDF-Datei: {file_path}")
    
    p = Path(file_path)
    text_content = ""
    
    # 1. Textextraktion versuchen
    if PyPDF2:
        try:
            with open(file_path, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                for page in reader.pages:
                    text_content += page.extract_text() + "\n"
        except Exception as e:
            print(f"⚠ Konnte Text aus PDF nicht extrahieren: {e}")
    else:
        print("⚠ PyPDF2 nicht installiert. Überspringe Textextraktion.")

    text_content = text_content.strip()
    if not text_content:
        text_content = "[Kein Textinhalt extrahierbar]"

    # 2. Datei als Attachment vorbereiten (Base64)
    try:
        with open(file_path, 'rb') as f:
            file_data = f.read()
            base64_data = base64.b64encode(file_data).decode('utf-8')
    except Exception as e:
        raise ValueError(f"Fehler beim Lesen der PDF-Datei für Attachment: {e}")

    # CouchDB Dokument mit Inline-Attachment
    mime_type = mimetypes.guess_type(file_path)[0] or "application/pdf"
    
    doc = {
        "filename": p.name,
        "content_type": "pdf",
        "extracted_text": text_content,
        "_attachments": {
            p.name: {
                "content_type": mime_type,
                "data": base64_data
            }
        }
    }

    print(f"✔ PDF erfolgreich verarbeitet (Textlänge: {len(text_content)} Zeichen).")
    return [doc]


# ---------------------------------------------------------
# Hauptfunktion
# ---------------------------------------------------------
def import_file_to_couchdb(file_path, db_url, db_name, user=None, password=None, id_column=None):
    auth = (user, password) if user and password else None

    # 1. DB sicherstellen
    if not ensure_database(db_url, db_name, auth):
        return

    # 2. Datentyp erkennen und laden
    p = Path(file_path)
    ext = p.suffix.lower()
    
    rows = []
    try:
        if ext == '.csv':
            rows = read_csv_data(file_path, id_column)
        elif ext == '.json':
            rows = read_json_data(file_path, id_column)
        elif ext == '.pdf':
            rows = read_pdf_data(file_path)
        else:
            print(f"✖ Nicht untersttztes Dateiformat: {ext}")
            print("Bitte nutze .csv, .json oder .pdf")
            return
    except Exception as e:
        print(f"\n✖ Fehler beim Lesen der Datei: {e}")
        return

    if not rows:
        print("⚠ Keine Daten zum Importieren gefunden.")
        return

    # 3. Bulk Upload
    payload = {"docs": rows}
    url = f"{db_url}/{db_name}/_bulk_docs"

    print(f"ℹ Sende {len(rows)} Dokumente an CouchDB...")
    try:
        response = requests.post(url, json=payload, auth=auth, timeout=30)
        print("Status:", response.status_code)
        
        # Kurze Zusammenfassung statt riesigem JSON-Dump bei Erfolg
        if response.status_code in (200, 201):
            res_json = response.json()
            # Prfen ob Fehler im Bulk-Response sind (CouchDB gibt 201 auch wenn einzelne Docs fehlschlagen)
            errors = [d for d in res_json if "error" in d]
            if not errors:
                print("✔ Alle Dokumente erfolgreich importiert.")
            else:
                print(f"⚠ {len(errors)} Dokumente konnten nicht importiert werden (z.B. ID-Konflikt).")
                print(f"Erster Fehler: {errors[0]}")
        else:
            print("Antwort:", response.text)

    except requests.exceptions.RequestException as e:
        print(f"✖ Netzwerkfehler beim Upload: {e}")


# ---------------------------------------------------------
# CLI
# ---------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(
        description="Universal CouchDB Importer (CSV, JSON & PDF) mit Auto-DB & Validierung"
    )

    parser.add_argument("--file", required=True, help="Pfad zur Datei (.csv, .json oder .pdf)")
    parser.add_argument("--db", required=True, help="Name der CouchDB-Datenbank")
    parser.add_argument("--url", default="http://localhost:5984", help="CouchDB-URL (Standard: http://localhost:5984)")
    parser.add_argument("--user", help="CouchDB Benutzername")
    parser.add_argument("--password", help="CouchDB Passwort")
    parser.add_argument("--id-column", help="Spalte/Feld, das als _id genutzt wird (optional)")

    args = parser.parse_args()

    import_file_to_couchdb(
        file_path=args.file,
        db_url=args.url,
        db_name=args.db,
        user=args.user,
        password=args.password,
        id_column=args.id_column
    )


if __name__ == "__main__":
    main()
