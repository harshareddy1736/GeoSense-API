import json
from pathlib import Path
from typing import Any

from .config import METADATA_DIR


def metadata_path(file_id: str) -> Path:
    return METADATA_DIR / f"{file_id}.json"


def save_metadata(file_id: str, data: dict[str, Any]) -> None:
    metadata_path(file_id).write_text(json.dumps(data, indent=2, default=str))


def load_metadata(file_id: str) -> dict[str, Any]:
    path = metadata_path(file_id)
    if not path.exists():
        raise FileNotFoundError(file_id)
    return json.loads(path.read_text())


def delete_metadata(file_id: str) -> None:
    path = metadata_path(file_id)
    if path.exists():
        path.unlink()
