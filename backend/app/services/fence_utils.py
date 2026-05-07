from math import cos, radians
from typing import Any

from shapely.geometry import shape
from shapely.ops import transform
from pyproj import CRS, Transformer


def feature_to_geometry(feature: dict[str, Any]):
    """把前端提交的 GeoJSON Feature 转为 shapely geometry。"""
    if feature.get("type") == "Feature":
        geometry = feature.get("geometry")
    else:
        geometry = feature
    if not geometry:
        raise ValueError("fence_geojson must contain a geometry")
    geom = shape(geometry)
    if geom.is_empty or geom.geom_type not in {"Polygon", "MultiPolygon"}:
        raise ValueError("fence geometry must be Polygon or MultiPolygon")
    return geom


def local_equal_area_transformer(lon: float, lat: float) -> Transformer:
    """为小范围地块创建本地投影，面积计算比直接经纬度更可靠。"""
    zone = int((lon + 180) / 6) + 1
    epsg = 32600 + zone if lat >= 0 else 32700 + zone
    return Transformer.from_crs(CRS.from_epsg(4326), CRS.from_epsg(epsg), always_xy=True)


def calculate_fence_info(feature: dict[str, Any]) -> dict[str, float | int]:
    geom = feature_to_geometry(feature)
    center = geom.centroid
    transformer = local_equal_area_transformer(center.x, center.y)
    projected = transform(transformer.transform, geom)
    coords = list(geom.exterior.coords) if geom.geom_type == "Polygon" else []
    return {
        "area_m2": round(float(projected.area), 2),
        "center_lon": round(float(center.x), 6),
        "center_lat": round(float(center.y), 6),
        "vertex_count": len(coords),
    }


def approximate_extent_meters(feature: dict[str, Any]) -> dict[str, float]:
    geom = feature_to_geometry(feature)
    minx, miny, maxx, maxy = geom.bounds
    mid_lat = (miny + maxy) / 2
    width_m = (maxx - minx) * 111_320 * cos(radians(mid_lat))
    height_m = (maxy - miny) * 110_540
    return {"width_m": abs(width_m), "height_m": abs(height_m)}
