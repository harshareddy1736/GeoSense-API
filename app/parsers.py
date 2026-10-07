from pathlib import Path
import zipfile

import geopandas as gpd
from shapely.geometry import Point, LineString, Polygon
from fastkml import kml


class ParseError(Exception):
    pass


def _read_kml(path: Path) -> gpd.GeoDataFrame:
    try:
        doc = kml.KML.parse(path)
        rows = []

        def walk(features):
            for feature in features:
                if hasattr(feature, "geometry") and feature.geometry is not None:
                    props = {}
                    name = getattr(feature, "name", None)
                    if name:
                        props["name"] = name
                    rows.append({"geometry": feature.geometry, **props})
                children = getattr(feature, "features", None)
                if children:
                    walk(children)

        walk(doc.features)
        if not rows:
            raise ParseError("KML contains no supported geometries")
        return gpd.GeoDataFrame(rows, geometry="geometry", crs="EPSG:4326")
    except Exception as exc:
        raise ParseError(f"Unable to parse KML: {exc}") from exc


def _read_shapefile_zip(path: Path) -> gpd.GeoDataFrame:
    try:
        with zipfile.ZipFile(path) as z:
            names = z.namelist()
            shp_names = [n for n in names if n.lower().endswith(".shp")]
            if not shp_names:
                raise ParseError("ZIP does not contain a .shp file")

            # Extract into a private temporary directory beside the uploaded file.
            target = path.parent / f"{path.stem}_extracted"
            target.mkdir(exist_ok=True)
            z.extractall(target)
            shp_path = target / shp_names[0]
            return gpd.read_file(shp_path)
    except zipfile.BadZipFile as exc:
        raise ParseError("Invalid ZIP file") from exc
    except ParseError:
        raise
    except Exception as exc:
        raise ParseError(f"Unable to parse Shapefile ZIP: {exc}") from exc


def read_geospatial_file(path: Path) -> gpd.GeoDataFrame:
    suffix = path.suffix.lower()

    if suffix == ".zip":
        gdf = _read_shapefile_zip(path)
    elif suffix == ".kml":
        gdf = _read_kml(path)
    elif suffix in {".geojson", ".json"}:
        try:
            gdf = gpd.read_file(path)
        except Exception as exc:
            raise ParseError(f"Unable to parse GeoJSON: {exc}") from exc
    else:
        raise ParseError("Unsupported file extension")

    if gdf.empty:
        raise ParseError("The uploaded dataset contains no features")

    if "geometry" not in gdf.columns:
        raise ParseError("Dataset does not contain a geometry column")

    return gdf


def geometry_type_name(geometry) -> str:
    if geometry is None:
        return "Unknown"
    return geometry.geom_type
