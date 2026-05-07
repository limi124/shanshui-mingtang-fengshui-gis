from pathlib import Path
from typing import Any

import numpy as np

from app.services.fence_utils import approximate_extent_meters


def mock_terrain_analysis(fence_geojson: dict[str, Any]) -> tuple[dict[str, Any], dict[str, str]]:
    """无真实 DEM 时使用稳定 mock 结果，保证前后端流程先跑通。"""
    extent = approximate_extent_meters(fence_geojson)
    scale = min(max((extent["width_m"] + extent["height_m"]) / 2000, 0.5), 3.0)
    mean_elevation = round(180 + scale * 18, 1)
    relief = round(95 + scale * 16, 1)
    mean_slope = round(6.8 + scale * 1.4, 1)

    metrics = {
        "mean_elevation": mean_elevation,
        "max_elevation": round(mean_elevation + relief * 0.58, 1),
        "min_elevation": round(mean_elevation - relief * 0.42, 1),
        "relief": relief,
        "mean_slope": mean_slope,
        "max_slope": round(mean_slope * 2.55, 1),
        "dominant_aspect": "东南",
        "terrain_position": "缓坡台地",
        "terrain_roughness": round(0.34 + scale * 0.04, 2),
    }
    spatial_pattern = {
        "back_mountain": "北侧地势相对较高，形成一定背靠格局；该结论当前基于 mock DEM 规则。",
        "front_open": "南侧坡度较缓且模拟开阔度较好，具备较好的前场展开条件。",
        "left_right_enclosure": "东西两侧存在温和高差，呈现一定围合但未形成过度封闭。",
        "water_relation": "暂未接入真实水系数据，当前为模拟结果；正式评估需叠加河流、水塘与汇水路径。",
        "road_relation": "暂未接入真实道路数据，当前为模拟结果；后续可接入道路 GeoJSON 分析可达性与干扰。",
    }
    return metrics, spatial_pattern


def analyze_dem_with_fence(dem_path: Path, fence_geojson: dict[str, Any]) -> tuple[dict[str, Any], dict[str, str]]:
    """预留真实 DEM 分析入口：读取 GeoTIFF、按围栏裁剪并计算高程/坡度/坡向。"""
    try:
        import geopandas as gpd
        import rasterio
        from rasterio.mask import mask
        from shapely.geometry import shape
    except Exception as exc:
        raise RuntimeError("DEM dependencies are not available") from exc

    if not dem_path.exists():
        raise FileNotFoundError(f"DEM file not found: {dem_path}")

    geometry = fence_geojson["geometry"] if fence_geojson.get("type") == "Feature" else fence_geojson
    geom = shape(geometry)

    with rasterio.open(dem_path) as dataset:
        gdf = gpd.GeoDataFrame(geometry=[geom], crs="EPSG:4326").to_crs(dataset.crs)
        clipped, transform = mask(dataset, gdf.geometry, crop=True, filled=False)
        data = clipped[0].astype("float64")
        valid = data.compressed() if np.ma.isMaskedArray(data) else data[np.isfinite(data)]
        if valid.size == 0:
            raise ValueError("DEM clip has no valid pixels")

        xres = abs(transform.a)
        yres = abs(transform.e)
        gy, gx = np.gradient(data.filled(np.nan), yres, xres)
        slope = np.degrees(np.arctan(np.sqrt(gx * gx + gy * gy)))
        aspect_degree = (np.degrees(np.arctan2(-gx, gy)) + 360) % 360

    mean_slope = float(np.nanmean(slope))
    max_slope = float(np.nanmax(slope))
    dominant_aspect = _aspect_name(float(np.nanmedian(aspect_degree)))
    relief = float(np.nanmax(valid) - np.nanmin(valid))
    terrain_position = "缓坡台地" if mean_slope < 10 else "坡地区域"

    metrics = {
        "mean_elevation": round(float(np.nanmean(valid)), 1),
        "max_elevation": round(float(np.nanmax(valid)), 1),
        "min_elevation": round(float(np.nanmin(valid)), 1),
        "relief": round(relief, 1),
        "mean_slope": round(mean_slope, 1),
        "max_slope": round(max_slope, 1),
        "dominant_aspect": dominant_aspect,
        "terrain_position": terrain_position,
        "terrain_roughness": round(float(np.nanstd(valid) / max(np.nanmean(valid), 1)), 2),
    }
    spatial_pattern = _basic_spatial_pattern(metrics)
    return metrics, spatial_pattern


def analyze_terrain(fence_geojson: dict[str, Any], dem_path: Path, use_mock: bool) -> tuple[dict[str, Any], dict[str, str]]:
    if use_mock:
        return mock_terrain_analysis(fence_geojson)
    try:
        return analyze_dem_with_fence(dem_path, fence_geojson)
    except Exception:
        return mock_terrain_analysis(fence_geojson)


def _aspect_name(degree: float) -> str:
    names = ["北", "东北", "东", "东南", "南", "西南", "西", "西北"]
    return names[int(((degree + 22.5) % 360) / 45)]


def _basic_spatial_pattern(metrics: dict[str, Any]) -> dict[str, str]:
    return {
        "back_mountain": "已基于真实 DEM 计算围栏内地形，但外围方向关系仍需后续邻域采样增强。",
        "front_open": "已基于真实 DEM 计算坡度，开阔度需接入周边缓冲区 DEM 与建筑/植被遮挡数据。",
        "left_right_enclosure": "左右围合关系预留真实 DEM 邻域剖面分析接口。",
        "water_relation": "暂未接入真实水系数据，需配置 VECTOR_WATER_PATH 后分析距离与汇水关系。",
        "road_relation": "暂未接入真实道路数据，需配置 VECTOR_ROAD_PATH 后分析道路关系。",
    }
