from typing import Any, Optional
from pydantic import BaseModel, Field


class Measurement(BaseModel):
    area_m2: Optional[float] = None
    length_m: Optional[float] = None


class FeatureMeasurement(BaseModel):
    feature_id: int
    geometry_type: str
    measurement: Optional[Measurement] = None
    status: str
    error: Optional[str] = None
    properties: dict[str, Any] = Field(default_factory=dict)


class FileInfo(BaseModel):
    id: str
    filename: str
    feature_count: int
    crs: str
    measurement_crs: str
    status: str
    geometry_types: dict[str, int]
    warnings: list[str] = Field(default_factory=list)


class AnalysisResponse(BaseModel):
    file_id: str
    feature_count: int
    geometry_types: dict[str, int]
    total_area_m2: float
    total_length_m: float
    bounding_box: list[float]
    centroid: list[float]
    source_crs: str
    measurement_crs: str
    warnings: list[str] = Field(default_factory=list)
