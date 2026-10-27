# SafeNova API

Run from the repository root:

```bash
python -m pip install -r requirements.txt
uvicorn backend.main:app --reload --port 8000
```

Endpoints:
- `GET /health` health check
- `GET /api/alerts` illustrative screening records for the dashboard
- `GET /api/areas` areas saved in this process
- `POST /api/areas` save a selected GeoJSON area

The current API returns demo alert records and stores areas in memory. It does not yet connect to official approval records, a trained AI model, soil HSG layers, or an elevation raster. In production, restrict CORS and persist areas in a database.
