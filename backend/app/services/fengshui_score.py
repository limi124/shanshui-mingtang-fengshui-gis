from typing import Any


def clamp_score(value: float) -> int:
    return int(max(0, min(100, round(value))))


def calculate_scores(
    metrics: dict[str, Any],
    spatial_pattern: dict[str, str],
    data_status: dict[str, dict[str, Any]] | None = None,
) -> dict[str, int]:
    """把 GIS 指标转换为传统环境格局评分，第一版采用透明规则。"""
    slope = float(metrics["mean_slope"])
    max_slope = float(metrics["max_slope"])
    relief = float(metrics["relief"])
    roughness = float(metrics["terrain_roughness"])
    aspect = str(metrics["dominant_aspect"])

    back_mountain_score = clamp_score(68 + min(relief / 4, 20) - max(slope - 15, 0))
    front_open_score = clamp_score(82 - slope * 1.1 - roughness * 12)
    enclosure_score = clamp_score(70 + min(relief / 12, 12) - max(roughness - 0.5, 0) * 30)
    water_status = (data_status or {}).get("water", {})
    water_score = int(water_status.get("score", 60))
    water_is_placeholder = bool(water_status.get("is_placeholder", True))
    aspect_light_score = 86 if aspect in {"南", "东南", "西南"} else 72 if aspect in {"东", "西"} else 58
    terrain_stability_score = clamp_score(92 - slope * 1.8 - max(max_slope - 25, 0) * 1.2)

    weights = {
        "back_mountain_score": 0.2,
        "front_open_score": 0.18,
        "enclosure_score": 0.17,
        "water_score": 0.12,
        "aspect_light_score": 0.15,
        "terrain_stability_score": 0.18,
    }
    raw_scores = {
        "back_mountain_score": back_mountain_score,
        "front_open_score": front_open_score,
        "enclosure_score": enclosure_score,
        "water_score": water_score,
        "aspect_light_score": aspect_light_score,
        "terrain_stability_score": terrain_stability_score,
    }
    if water_is_placeholder:
        weights.pop("water_score")

    weight_sum = sum(weights.values())
    overall_score = clamp_score(sum(raw_scores[key] * weight for key, weight in weights.items()) / weight_sum)

    return {
        "back_mountain_score": back_mountain_score,
        "front_open_score": front_open_score,
        "enclosure_score": enclosure_score,
        "water_score": water_score,
        "aspect_light_score": aspect_light_score,
        "terrain_stability_score": terrain_stability_score,
        "overall_score": overall_score,
    }
