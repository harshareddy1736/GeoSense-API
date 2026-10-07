from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
UPLOAD_DIR = BASE_DIR / "uploads"
METADATA_DIR = BASE_DIR / "geosense_metadata"
MAX_FILE_SIZE_MB = 25

ALLOWED_EXTENSIONS = {".zip", ".kml", ".geojson", ".json"}

UPLOAD_DIR.mkdir(exist_ok=True)
METADATA_DIR.mkdir(exist_ok=True)
