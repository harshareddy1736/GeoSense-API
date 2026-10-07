from .models import FeatureMeasurement, Measurement


SUPPORTED = {"Polygon", "MultiPolygon", "LineString", "MultiLineString", "Point", "MultiPoint"}


def measure_feature(index: int, row) -> FeatureMeasurement:
    geom = row.geometry
    geom_type = getattr(geom, "geom_type", "Unknown")
    props = {}

    for key, value in row.items():
        if key != "geometry":
            try:
                if value is None or isinstance(value, (str, int, float, bool)):
                    props[str(key)] = value
                else:
                    props[str(key)] = str(value)
            except Exception:
                props[str(key)] = "<unserializable>"

    if geom is None or geom.is_empty:
        return FeatureMeasurement(
            feature_id=index,
            geometry_type=geom_type,
            status="SKIPPED",
            error="Empty geometry",
            properties=props,
        )

    if not geom.is_valid:
        return FeatureMeasurement(
            feature_id=index,
            geometry_type=geom_type,
            status="INVALID_GEOMETRY",
            error="Geometry failed validity check",
            properties=props,
        )

    if geom_type in {"Polygon", "MultiPolygon"}:
        return FeatureMeasurement(
            feature_id=index,
            geometry_type=geom_type,
            measurement=Measurement(area_m2=round(float(geom.area), 6)),
            status="MEASURED",
            properties=props,
        )

    if geom_type in {"LineString", "MultiLineString"}:
        return FeatureMeasurement(
            feature_id=index,
            geometry_type=geom_type,
            measurement=Measurement(length_m=round(float(geom.length), 6)),
            status="MEASURED",
            properties=props,
        )

    if geom_type in {"Point", "MultiPoint"}:
        return FeatureMeasurement(
            feature_id=index,
            geometry_type=geom_type,
            measurement=None,
            status="NO_MEASUREMENT_REQUIRED",
            properties=props,
        )

    return FeatureMeasurement(
        feature_id=index,
        geometry_type=geom_type,
        status="UNSUPPORTED_GEOMETRY",
        error=f"Measurement is not implemented for {geom_type}",
        properties=props,
    )
