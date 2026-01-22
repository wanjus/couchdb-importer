#!/usr/bin/env python3
"""
 * author Saquib Shaikh
 * created on 20-01-2026-20h-23m
 * github: https://github.com/saquibshaikh14
 * copyright 2026
"""

import csv
import json
import argparse
import requests
from pathlib import Path

# ---------------------------------------------------------
# Hilfsfunktion: Prfen, ob DB existiert – sonst erstellen
# ---------------------------------------------------------
def ensure_database(db_url, db_name, auth=None):
    url = f"{db_url}/{db_name}"
    try:
        r = requests.get(url, auth=auth)
    except requests.exceptions.RequestException as e:
        print(f"✖ Verbindungsfehler zu CouchDB ({url}): {e}")
        return False

    if r.status_code == 200:
        print(f"✔ Datenbank '{db_name}' existiert bereits.")
        return True

    if r.status_code == 404:
        print(f"⚠ Datenbank '{db_name}' existiert nicht – wird erstellt...")
        r = requests.put(url, auth=auth)
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
    
    # Spalten validieren
    with open(file_path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        columns = reader.fieldnames
        if id_column and id_column not in columns:
            raise ValueError(f"Die ID-Spalte '{id_column}' existiert nicht in der CSV ({columns}).")

    rows = []
    with open(file_path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        # Zeilen zhlen fr Fortschritt (ungefhr)
        total = sum(1 for _ in open(file_path, encoding='utf-8')) - 1
        f.seek(0)
        next(reader) # Header berspringen

        for i, row in enumerate(reader, start=1):
            # ID setzen
            doc_id = row[id_column] if id_column else str(i)
            # Falls noch keine _id da ist, setzen
            if "_id" not in row:
                row["_id"] = doc_id
            
            rows.append(row)
            print(f"→ Verarbeite Zeile {i}/{total}", end="\r")
    
    print("\n✔ CSV vollstndig eingelesen.")
    return rows


# ---------------------------------------------------------
# Logik: JSON einlesen
# ---------------------------------------------------------
def read_json_data(file_path, id_column=None):
    print(f"ℹ Lese JSON-Datei: {file_path}")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    rows = []
    
    # Fall 1: Format {"docs": [...]} (CouchDB Standard)
    if isinstance(data, dict) and "docs" in data:
        print("ℹ Erkanntes Format: {'docs': [...]}")
        rows = data["docs"]
    
    # Fall 2: Format [...] (Liste von Objekten)
    elif isinstance(data, list):
        print("ℹ Erkanntes Format: Liste [...]")
        # Smart Wrap: Prüfen, ob die Elemente Objekte sind. Wenn nicht (z.B. Strings), verpacken.
        cleaned_rows = []
        for item in data:
            if isinstance(item, dict):
                cleaned_rows.append(item)
            else:
                # "Action" -> {"value": "Action"}
                cleaned_rows.append({"value": item})
        
        if len(cleaned_rows) > 0 and cleaned_rows != data:
             print("⚠ Liste enthielt einfache Werte (Strings/Zahlen). Habe sie automatisch in {'value': ...} Objekte umgewandelt.")
        
        rows = cleaned_rows
    
    # Fall 3: Einzelnes Objekt {...}
    elif isinstance(data, dict):
        print("ℹ Erkanntes Format: Einzelnes Objekt {...}")
        rows = [data]
    else:
        raise ValueError("Unbekanntes JSON-Format. Erwarte Liste oder {'docs': [...]}.")

    # Optional: IDs anpassen/setzen, falls id_column gewnscht ist
    if id_column:
        print(f"ℹ Verwende Feld '{id_column}' als _id...")
        for i, doc in enumerate(rows):
            if id_column in doc:
                doc["_id"] = str(doc[id_column])
            # Falls die Spalte fehlt, optional warnen oder ignorieren. 
            # Hier: Wir lassen es so, CouchDB generiert dann eine UUID wenn _id fehlt.

    print(f"✔ {len(rows)} Dokumente aus JSON geladen.")
    return rows


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
        else:
            print(f"✖ Nicht untersttztes Dateiformat: {ext}")
            print("Bitte nutze .csv oder .json")
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
        response = requests.post(url, json=payload, auth=auth)
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
        description="Universal CouchDB Importer (CSV & JSON) mit Auto-DB & Validierung"
    )

    parser.add_argument("--file", required=True, help="Pfad zur Datei (.csv oder .json)")
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
