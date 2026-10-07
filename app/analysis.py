from collections import Counter
import geopandas as gpd

from .measurements import measure_feature


def analyze(gdf: gpd.GeoDataFrame, projected: gpd.GeoDataFrame, source_crs: str, measurement_crs: str):
    results = [measure_feature(i, row) for i, (_, row) in enumerate(projected.iterrows())]

    type_counts = Counter(str(g) for g in gdf.geometry.geom_type)
    total_area = sum((r.measurement.area_m2 or 0) for r in results if r.measurement)
    total_length = sum((r.measurement.length_m or 0) for r in results if r.measurement)

    source4326 = gdf.to_crs("EPSG:4326") if gdf.crs else gdf.set_crs("EPSG:3857").to_crs("EPSG:4326")
    bounds = [round(float(x), 8) for x in source4326.total_bounds]
    c = source4326.geometry.union_all().centroid

    warnings = []
    if gdf.crs is None:
        warnings.append("Source CRS was missing; EPSG:3857 fallback was used. Results may be approximate.")
    invalid_count = sum(1 for r in results if r.status == "INVALID_GEOMETRY")
    if invalid_count:
        warnings.append(f"{invalid_count} feature(s) have invalid geometry and were skipped.")
    unsupported_count = sum(1 for r in results if r.status == "UNSUPPORTED_GEOMETRY")
    if unsupported_count:
        warnings.append(f"{unsupported_count} feature(s) use unsupported geometry types.")

    return {
        "results": results,
        "geometry_types": dict(type_counts),
        "total_area_m2": round(total_area, 6),
        "total_length_m": round(total_length, 6),
        "bounding_box": bounds,
        "centroid": [round(float(c.x), 8), round(float(c.y), 8)],
        "source_crs": source_crs,
        "measurement_crs": measurement_crs,
        "warnings": warnings,
    }
