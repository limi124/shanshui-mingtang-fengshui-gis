from pathlib import Path
from typing import Any


def build_data_status(
    *,
    dem_path: Path,
    water_path: Path,
    road_path: Path,
    use_mock: bool,
) -> dict[str, dict[str, Any]]:
    """Describe which local datasets are really available for this run.

    Sensitive fence coordinates are not included here. The status is only used
    to keep reports honest when a layer such as water or road data is missing.
    """
    dem_exists = dem_path.exists()
    water_exists = water_path.exists()
    road_exists = road_path.exists()

    return {
        "dem": {
            "status": "mock" if use_mock or not dem_exists else "ready",
            "available": dem_exists and not use_mock,
            "is_placeholder": use_mock or not dem_exists,
            "message": "正在使用真实 DEM 数据。" if dem_exists and not use_mock else "当前使用 mock DEM 或 DEM 不可用。",
        },
        "water": {
            "status": "pending_integration" if water_exists else "missing",
            "available": water_exists,
            "is_placeholder": True,
            "score_policy": "neutral_placeholder_excluded_from_overall",
            "message": (
                "检测到本地水系文件，但当前 MVP 尚未启用水系空间计算。"
                if water_exists
                else "未检测到真实水系数据，得水条件仅显示中性占位分，不参与综合分确定性计算。"
            ),
        },
        "road": {
            "status": "pending_integration" if road_exists else "missing",
            "available": road_exists,
            "is_placeholder": True,
            "message": (
                "检测到本道路文件，但当前 MVP 尚未启用道路空间计算。"
                if road_exists
                else "未检测到真实道路数据，道路关系仅作为待接入项展示。"
            ),
        },
    }
