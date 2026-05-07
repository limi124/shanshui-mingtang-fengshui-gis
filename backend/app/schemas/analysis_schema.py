from typing import Any, Literal

from pydantic import BaseModel, Field


class FenceAnalysisRequest(BaseModel):
    fence_geojson: dict[str, Any] = Field(..., description="用户电子围栏 GeoJSON Feature")
    analysis_mode: Literal["environment", "terrain", "culture"] = "environment"
    use_mock: bool = True


class FenceInfo(BaseModel):
    area_m2: float
    center_lon: float
    center_lat: float
    vertex_count: int


class TerrainMetrics(BaseModel):
    mean_elevation: float
    max_elevation: float
    min_elevation: float
    relief: float
    mean_slope: float
    max_slope: float
    dominant_aspect: str
    terrain_position: str
    terrain_roughness: float


class SpatialPattern(BaseModel):
    back_mountain: str
    front_open: str
    left_right_enclosure: str
    water_relation: str
    road_relation: str


class FengshuiScores(BaseModel):
    back_mountain_score: int
    front_open_score: int
    enclosure_score: int
    water_score: int
    aspect_light_score: int
    terrain_stability_score: int
    overall_score: int


class DataStatus(BaseModel):
    dem: dict[str, Any]
    water: dict[str, Any]
    road: dict[str, Any]


class FenceAnalysisResponse(BaseModel):
    fence_info: FenceInfo
    terrain_metrics: TerrainMetrics
    spatial_pattern: SpatialPattern
    scores: FengshuiScores
    data_status: DataStatus
    report: str
    fortune_module: dict[str, Any]
    disclaimer: str
