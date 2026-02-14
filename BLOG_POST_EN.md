# 🚀 Stop Stressing Over CouchDB Imports: Load CSV & JSON in Seconds

*"I'll just quickly import some test data..."* – every developer has said this. And every developer knows it often turns into an hour of frustration: broken JSON formats, encoding errors in CSVs, or endless `curl` commands that are impossible to remember.

We – **Team Wanju & KI Gemini** – had enough. That's why we built a tool that just works.

## The Problem

CouchDB is great, but getting data into it can be a pain.
*   **Fauxton** (the web UI) is okay for single documents, but tedious for bulk uploads.
*   **Curl** is powerful, but heaven help you if you forget a quote on Windows.
*   **Custom scripts** are rewritten every time and break at the first special character.

## The Solution: CouchDB-Importer

Our [CouchDB-Importer](https://github.com/wanjus/couchdb-importer) is a "Swiss Army Knife" for data imports, written in Python. It's pragmatic, robust, and open source.

### What can it do?

1.  **CSV, JSON & PDF Support:** Whether it's an Excel export, an API dump, or a document archive, the tool handles it all.
2.  **PDF Intelligence:** PDFs aren't just attached as binary files; the script also tries to extract text content to make it searchable within CouchDB.
3.  **JSON & JSONL:** In addition to standard JSON lists, the popular JSON Lines format (`.jsonl`) is now supported.
4.  **Auto-DB:** If the target database doesn't exist, it's created automatically. No more manual `PUT` requests.
5.  **Robust:** Network timeouts prevent the script from hanging, and simple data types are automatically wrapped into objects.
6.  **Feedback:** A clean progress bar shows you exactly what's happening.

## Quick Start

All you need is Python.

```bash
# 1. Clone the repo
git clone https://github.com/wanjus/couchdb-importer.git
cd couchdb-importer

# 2. Install dependencies
pip install -r requirements.txt

# 3. Import data (Example)
python CouchDB-Importer.py --file my_data.csv --db testdb --user admin --password secret
```

That's it. Your data is in.

## Join in!

The project is **Open Source (MIT License)**. We welcome GitHub stars, issues, or pull requests.

👉 **[Go to GitHub Repository](https://github.com/wanjus/couchdb-importer)**

---
*Developed with ❤️ and Python by Jürgen (Wanju) and Gemini.*
