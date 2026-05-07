from pathlib import Path
from typing import Any

from shapely.geometry import shape

from app.services.fengshui_score import clamp_score


def analyze_water_relation(fence_geojson: dict[str, Any], water_path: Path) -> dict[str, Any]:
    """Analyze local river polygon data around the user fence.

    The function reads only features around the fence bbox instead of loading a
    nationwide water layer into memory. It returns status metadata, a readable
    relation sentence, and a rule-based score.
    """
    if not water_path.exists():
        return _missing_status()

    try:
        import geopandas as gpd
    except Exception:
        status = _missing_status()
        status.update({
            "status": "dependency_missing",
            "message": "已配置水系数据，但 geopandas 不可用，暂无法计算真实得水关系。",
        })
        return status

    geometry = fence_geojson["geometry"] if fence_geojson.get("type") == "Feature" else fence_geojson
    fence_geom = shape(geometry)
    if fence_geom.is_empty:
        raise ValueError("Fence geometry is empty")

    water_gdf = _read_nearby_water(gpd, water_path, fence_geom.bounds)
    if water_gdf.empty:
        return {
            "status": "ready",
            "available": True,
            "is_placeholder": False,
            "score_policy": "real_vector_water_rule_score",
            "nearest_distance_m": None,
            "direction": "未识别",
            "intersects": False,
            "score": 52,
            "message": "已接入真实水系面数据，但围栏周边约 50 km 范围内未检索到河流面，得水条件偏弱；仍建议结合线状水系、沟渠和现场排水复核。",
        }

    fence_gdf = gpd.GeoDataFrame(geometry=[fence_geom], crs="EPSG:4326")
    if water_gdf.crs is None:
        water_gdf = water_gdf.set_crs("EPSG:4326")
    water_gdf = water_gdf.to_crs("EPSG:4326")

    intersects = bool(water_gdf.intersects(fence_geom).any())
    fence_m = fence_gdf.to_crs("EPSG:3857")
    water_m = water_gdf.to_crs("EPSG:3857")
    distances = water_m.distance(fence_m.geometry.iloc[0])
    nearest_idx = distances.idxmin()
    nearest_distance_m = float(distances.loc[nearest_idx])
    nearest_geom = water_gdf.loc[nearest_idx].geometry
    direction = _direction_name(fence_geom.centroid, nearest_geom.centroid)
    score = _score_water_relation(nearest_distance_m, intersects)

    relation = _relation_text(nearest_distance_m, direction, intersects, score)
    return {
        "status": "ready",
        "available": True,
        "is_placeholder": False,
        "score_policy": "real_vector_water_rule_score",
        "nearest_distance_m": round(nearest_distance_m, 1),
        "direction": direction,
        "intersects": intersects,
        "score": score,
        "message": relation,
    }


def _read_nearby_water(gpd, water_path: Path, bounds: tuple[float, float, float, float]):
    minx, miny, maxx, maxy = bounds
    width = max(maxx - minx, 0.01)
    height = max(maxy - miny, 0.01)
    # Expand gradually. The last pass is roughly a broad regional search.
    for multiplier in [2, 5, 10, 25, 60]:
        pad_x = width * multiplier
        pad_y = height * multiplier
        bbox = (minx - pad_x, miny - pad_y, maxx + pad_x, maxy + pad_y)
        water_gdf = gpd.read_file(water_path, bbox=bbox)
        if not water_gdf.empty:
            return water_gdf
    return gpd.read_file(water_path, rows=0)


def _score_water_relation(distance_m: float, intersects: bool) -> int:
    if intersects:
        # Water crossing the fence may be visually favorable, but it also raises
        # construction, flooding, and setback constraints.
        return 62
    if distance_m <= 50:
        return 68
    if distance_m <= 1000:
        return 86
    if distance_m <= 3000:
        return 78
    if distance_m <= 8000:
        return 66
    return clamp_score(58 - min((distance_m - 8000) / 3000, 12))


def _relation_text(distance_m: float, direction: str, intersects: bool, score: int) -> str:
    if intersects:
        return (
            f"真实水系面数据表明：围栏范围与河流/水体面存在相交，得水评分 {score}。"
            "该情况需重点核验洪水位、退让红线、排水组织与建设管控，不宜直接按文化意象作正向判断。"
        )
    if distance_m <= 1000:
        level = "距离适中，具备较好的近水环境条件"
    elif distance_m <= 3000:
        level = "距离较近，可作为周边水系环境参考"
    elif distance_m <= 8000:
        level = "距离偏远，得水关系较弱"
    else:
        level = "距离较远，水系对场地格局影响有限"
    return f"真实水系面数据表明：最近河流/水体面位于围栏{direction}侧约 {distance_m:.0f} m，{level}，得水评分 {score}。"


def _direction_name(origin, target) -> str:
    dx = target.x - origin.x
    dy = target.y - origin.y
    if abs(dx) < 1e-9 and abs(dy) < 1e-9:
        return "内部"
    import math

    degree = (math.degrees(math.atan2(dx, dy)) + 360) % 360
    names = ["北", "东北", "东", "东南", "南", "西南", "西", "西北"]
    return names[int(((degree + 22.5) % 360) / 45)]


def _missing_status() -> dict[str, Any]:
    return {
        "status": "missing",
        "available": False,
        "is_placeholder": True,
        "score_policy": "neutral_placeholder_excluded_from_overall",
        "nearest_distance_m": None,
        "direction": "未识别",
        "intersects": False,
        "score": 60,
        "message": "未检测到真实水系数据，得水条件仅显示中性占位分，不参与综合分确定性计算。",
    }
