import math
import geopandas as gpd


def crs_label(crs) -> str:
    if crs is None:
        return "UNKNOWN"
    return crs.to_string()


def choose_measurement_crs(gdf: gpd.GeoDataFrame):
    if gdf.crs is None:
        # A missing CRS cannot be safely interpreted as geographic coordinates.
        # Use Web Mercator only as a clearly-labelled fallback.
        return "EPSG:3857"

    if not gdf.crs.is_geographic:
        return gdf.crs

    centroid = gdf.to_crs("EPSG:4326").geometry.union_all().centroid
    lon, lat = centroid.x, centroid.y

    zone = int((lon + 180) / 6) + 1
    zone = max(1, min(zone, 60))

    epsg = 32600 + zone if lat >= 0 else 32700 + zone
    return f"EPSG:{epsg}"


def project_for_measurement(gdf: gpd.GeoDataFrame):
    target = choose_measurement_crs(gdf)
    if isinstance(target, str):
        projected = gdf.to_crs(target)
    elif gdf.crs == target:
        projected = gdf
    else:
        projected = gdf.to_crs(target)
    return projected, crs_label(gdf.crs), crs_label(projected.crs)
