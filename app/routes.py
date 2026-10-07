from pathlib import Path
from uuid import uuid4
import shutil

from fastapi import APIRouter, File, HTTPException, UploadFile

from .analysis import analyze
from .config import ALLOWED_EXTENSIONS, MAX_FILE_SIZE_MB, UPLOAD_DIR
from .crs_engine import project_for_measurement, crs_label
from .models import AnalysisResponse, FileInfo
from .parsers import ParseError, read_geospatial_file
from .storage import delete_metadata, load_metadata, save_metadata

router = APIRouter(prefix="/api")


def _file_path(file_id: str, suffix: str) -> Path:
    return UPLOAD_DIR / f"{file_id}{suffix}"


@router.post("/files/", response_model=FileInfo)
async def upload_file(file: UploadFile = File(...)):
    original = Path(file.filename or "")
    suffix = original.suffix.lower()

    if suffix not in ALLOWED_EXTENSIONS:
        raise HTTPException(400, "Unsupported file type. Use ZIP, KML or GeoJSON.")

    file_id = str(uuid4())
    target = _file_path(file_id, suffix)

    size = 0
    try:
        with target.open("wb") as out:
            while chunk := await file.read(1024 * 1024):
                size += len(chunk)
                if size > MAX_FILE_SIZE_MB * 1024 * 1024:
                    target.unlink(missing_ok=True)
                    raise HTTPException(413, f"File exceeds {MAX_FILE_SIZE_MB} MB limit.")
                out.write(chunk)

        gdf = read_geospatial_file(target)
        projected, source_crs, measurement_crs = project_for_measurement(gdf)
        report = analyze(gdf, projected, source_crs, measurement_crs)

        metadata = {
            "id": file_id,
            "filename": file.filename,
            "feature_count": len(gdf),
            "crs": source_crs,
            "measurement_crs": measurement_crs,
            "status": "COMPLETED",
            "geometry_types": report["geometry_types"],
            "warnings": report["warnings"],
            "analysis": {
                "total_area_m2": report["total_area_m2"],
                "total_length_m": report["total_length_m"],
                "bounding_box": report["bounding_box"],
                "centroid": report["centroid"],
            },
        }
        save_metadata(file_id, metadata)
        return metadata

    except HTTPException:
        raise
    except ParseError as exc:
        target.unlink(missing_ok=True)
        raise HTTPException(422, str(exc))
    except Exception as exc:
        target.unlink(missing_ok=True)
        raise HTTPException(500, f"Processing failed: {exc}")


@router.get("/files/{file_id}/", response_model=FileInfo)
def file_info(file_id: str):
    try:
        return load_metadata(file_id)
    except FileNotFoundError:
        raise HTTPException(404, "File not found")


@router.get("/files/{file_id}/measurements/")
def measurements(file_id: str):
    try:
        meta = load_metadata(file_id)
    except FileNotFoundError:
        raise HTTPException(404, "File not found")

    path_candidates = list(UPLOAD_DIR.glob(f"{file_id}.*"))
    if not path_candidates:
        raise HTTPException(404, "Uploaded data is no longer available")

    try:
        gdf = read_geospatial_file(path_candidates[0])
        projected, source_crs, measurement_crs = project_for_measurement(gdf)
        report = analyze(gdf, projected, source_crs, measurement_crs)
        return {
            "file_id": file_id,
            "filename": meta["filename"],
            "source_crs": source_crs,
            "measurement_crs": measurement_crs,
            "units": "meters",
            "features": [r.model_dump() for r in report["results"]],
        }
    except Exception as exc:
        raise HTTPException(500, f"Measurement calculation failed: {exc}")


@router.get("/files/{file_id}/analysis/", response_model=AnalysisResponse)
def analysis(file_id: str):
    try:
        meta = load_metadata(file_id)
    except FileNotFoundError:
        raise HTTPException(404, "File not found")

    a = meta["analysis"]
    return {
        "file_id": file_id,
        "feature_count": meta["feature_count"],
        "geometry_types": meta["geometry_types"],
        "total_area_m2": a["total_area_m2"],
        "total_length_m": a["total_length_m"],
        "bounding_box": a["bounding_box"],
        "centroid": a["centroid"],
        "source_crs": meta["crs"],
        "measurement_crs": meta["measurement_crs"],
        "warnings": meta["warnings"],
    }


@router.delete("/files/{file_id}/")
def delete_file(file_id: str):
    try:
        load_metadata(file_id)
    except FileNotFoundError:
        raise HTTPException(404, "File not found")

    for path in UPLOAD_DIR.glob(f"{file_id}*"):
        if path.is_dir():
            shutil.rmtree(path, ignore_errors=True)
        else:
            path.unlink(missing_ok=True)
    delete_metadata(file_id)
    return {"id": file_id, "status": "DELETED"}
