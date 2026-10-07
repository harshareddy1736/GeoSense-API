# GeoSense API — Intelligent Geospatial File Measurement Service

GeoSense is a FastAPI backend that uploads, validates, analyzes, and measures geospatial files.

## Why this version is different

Beyond the basic assignment requirements, GeoSense adds:

- Shapefile ZIP and KML support
- Optional GeoJSON support as a bonus
- Automatic CRS detection and projected CRS selection
- Area/length calculations in metric units instead of latitude/longitude degrees
- Per-feature geometry validation with graceful error reporting
- Geometry type distribution and dataset summary statistics
- Bounding box and centroid calculation
- Coordinate transformation metadata
- Measurement confidence/status for each feature
- Server-side file validation and size limits
- Unique file IDs and persistent JSON metadata
- Health endpoint
- OpenAPI/Swagger documentation
- Clean service/repository/parser architecture
- Automated API tests

## Architecture

```text
Client
  |
  v
FastAPI Routes
  |
  +--> Upload Validator
  |
  +--> Geospatial Parser
  |       +--> Shapefile ZIP
  |       +--> KML
  |       +--> GeoJSON (bonus)
  |
  +--> CRS Engine
  |       +--> Geographic CRS -> local projected CRS
  |
  +--> Measurement Engine
  |       +--> Polygon -> area
  |       +--> LineString -> length
  |       +--> Point -> no measurement
  |
  +--> Analysis Engine
          +--> summary
          +--> bbox
          +--> centroid
          +--> geometry statistics
          +--> validation warnings
```

## Requirements

- Python 3.11+
- GDAL/GeoPandas dependencies supported by your OS

## Setup

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate

pip install -r requirements.txt
uvicorn app.main:app --reload
```

Open:

- Swagger UI: http://127.0.0.1:8000/docs
- Health: http://127.0.0.1:8000/health

## API

### 1. Upload and process

`POST /api/files/`

Form field:

```text
file=<geospatial file>
```

Accepted:

- `.zip` containing a Shapefile
- `.kml`
- `.geojson` / `.json` (bonus)

### 2. File information

`GET /api/files/{id}/`

Returns metadata, CRS, feature count, summary and processing status.

### 3. Measurements

`GET /api/files/{id}/measurements/`

Returns per-feature measurements and graceful errors.

### 4. Dataset analytics

`GET /api/files/{id}/analysis/`

Returns:

- geometry counts
- total measured area
- total measured length
- bounding box
- centroid
- source/projected CRS
- warnings

### 5. Delete

`DELETE /api/files/{id}/`

Deletes the uploaded dataset and metadata.

## Example measurement response

```json
{
  "file_id": "8d3d...",
  "measurement_crs": "EPSG:32643",
  "units": "meters",
  "features": [
    {
      "feature_id": 0,
      "geometry_type": "Polygon",
      "measurement": {
        "area_m2": 15342.28
      },
      "status": "MEASURED"
    }
  ]
}
```

## CRS strategy

If the source CRS is geographic, such as EPSG:4326, GeoSense chooses a local UTM zone from the dataset centroid and transforms the geometries before calculating measurements.

If the source CRS is already projected, the API uses it directly when its units are metric.

This prevents incorrect calculations in latitude/longitude degrees.

## Design decisions

1. FastAPI was selected for a lightweight, typed API with automatic OpenAPI documentation.
2. GeoPandas/Shapely provide robust geometry handling.
3. PyProj handles CRS transformations.
4. Uploaded files are isolated by generated UUIDs.
5. Processing errors are returned per feature instead of crashing the entire request.
6. JSON metadata keeps the project easy to run locally without requiring PostgreSQL/PostGIS.

## Future scope

- PostGIS storage
- background processing with Celery/RQ
- map visualization dashboard
- spatial indexing
- authentication and API keys
- S3/object storage
- batch uploads
- asynchronous processing for very large datasets
- PDF/CSV measurement reports
- elevation-aware 3D measurements

## Project structure

```text
geosense_api/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── config.py
│   ├── models.py
│   ├── storage.py
│   ├── parsers.py
│   ├── crs_engine.py
│   ├── measurements.py
│   ├── analysis.py
│   └── routes.py
├── tests/
│   └── test_api.py
├── uploads/
├── requirements.txt
├── .gitignore
└── README.md
```
