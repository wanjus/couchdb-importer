  # CouchDB-Importer.py 
  # jetzt ein echtes Schweizer Taschenmesser für deine Datenimporte:

     1. CSV-Support mit Spaltenvalidierung und Fortschrittsanzeige.
  
     2. JSON-Support für verschiedene Strukturen (docs-Wrapper oder reine Listen).
      
     3. Fehlertoleranz durch automatisches Verpacken von einfachen Strings/Zahlen in Objekte.
      
     4. Auto-DB-Erstellung, falls die Zieldatenbank noch nicht existiert. 🚀

# Installation

## git clone https://github.com/wanjus/couchdb-importer.git 

## Beispiele:

* python CouchDB‑Importer.py
  
  usage:
  CouchDB‑Importer.py [-h] --file FILE --db DB [--url URL] [--user USER] [--password PASSWORD]
                           [--id-column ID_COLUMN]
  CouchDB‑Importer.py: error: the following arguments are required: --file, --db

* import für *.json Datei:
  python CouchDB‑Importer.py --file test.json --db test --user admin --password admin

* import für *.csv Datei:
  python CouchDB‑Importer.py --file test.csv --db test --user admin --password admin
