"""
 * author Saquib Shaikh
 * created on 20-01-2026-19h-07m
 * github: https://github.com/saquibshaikh14
 * copyright 2026
"""

import csv
import json
import requests # type: ignore
from pathlib import Path

def import_csv_to_couchdb(
    csv_file,
    db_url,
    db_name,
    user=None,
    password=None,
    id_column=None
):
    # CSV einlesen
    rows = []
    with open(csv_file, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader):
            # ID bestimmen
            doc_id = row[id_column] if id_column else str(i + 1)
            row["_id"] = doc_id
            rows.append(row)

    # Bulk-Body
    payload = {"docs": rows}

    # Auth optional
    auth = (user, password) if user and password else None

    # POST an CouchDB
    url = f"{db_url}/{db_name}/_bulk_docs"
    response = requests.post(url, json=payload, auth=auth)

    print("Status:", response.status_code)
    print("Antwort:", response.text)


# Beispielaufruf:
if __name__ == "__main__":
    import_csv_to_couchdb(
        csv_file="test.csv",
        db_url="http://localhost:5984",
        db_name="test",
        user="juergen",          # oder None
        password="tantetom",     # oder None
        id_column="id"         # optional: Spalte, die als _id genutzt wird
    )
