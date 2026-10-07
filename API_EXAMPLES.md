# Quick API Examples

Start the server:

```bash
uvicorn app.main:app --reload
```

Upload:

```bash
curl -X POST "http://127.0.0.1:8000/api/files/" \
  -F "file=@sample.geojson"
```

Then use the returned `id`:

```bash
curl "http://127.0.0.1:8000/api/files/<id>/"
curl "http://127.0.0.1:8000/api/files/<id>/measurements/"
curl "http://127.0.0.1:8000/api/files/<id>/analysis/"
```

Delete:

```bash
curl -X DELETE "http://127.0.0.1:8000/api/files/<id>/"
```
