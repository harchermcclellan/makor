# Makor — Biblical & Talmudic Name Explorer

A Flask web app for exploring names through their biblical, talmudic, and #TODO linguistic origins.

## Project Structure

```
makor/
├── app.py              # Flask server (routes + mock data)
└── templates/
    └── index.html      # Single-page frontend (vanilla JS + CSS)
```

## Setup

```bash
cd makor
pip install flask
python app.py
```

Open http://localhost:8000 in your browser. Search "Miriam" or "Ezra" to see the mock data.

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/` | Serves the frontend |
| GET | `/api/names/<name>` | Look up a name's full entry |
| GET | `/api/names/suggest?q=` | Autocomplete suggestions |
| GET | `/api/sources` | List available source categories |
| GET | `/api/health` | Health check |

## Next Steps

### Disambiguating names outside of biblical Main Characters
Currently the search uses Sefaria Topics for an exact match; Use Sefaria's elasticsearch to disambiguate for more robust responses.
Example: Serah returns nothing because the Sefaria Topic for Serah is "Serah the Daughter of Asher" - you'll need to use elasticsearch to get the Primary Title for the Serah Topic, then run a second search for her by Topic title. Furthermore, Beriah (Serah's brother) doesn't have a dedicated Topic, but we should still return all the relevant passages about him if possible.

### Caching information
Realtime requests work if you're requesting one name at a time, but we might want to get information recursively, create a complex family tree, or store information Wiki style -- to do that, we'd need to cache at least the sefaria responses, or more likely the processed and interpreted data.