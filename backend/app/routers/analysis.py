from fastapi import APIRouter, HTTPException

from app.core.config import settings
from app.schemas.analysis_schema import FenceAnalysisRequest, FenceAnalysisResponse
from app.services.data_status import build_data_status
from app.services.fence_utils import calculate_fence_info
from app.services.fengshui_score import calculate_scores
from app.services.fortune_module import get_fortune_placeholder
from app.services.llm_report_generator import generate_llm_report
from app.services.report_generator import DISCLAIMER, generate_report
from app.services.terrain_analysis import analyze_terrain
from app.services.water_analysis import analyze_water_relation

router = APIRouter()


@router.post("/fence", response_model=FenceAnalysisResponse)
def analyze_fence(payload: FenceAnalysisRequest):
    try:
        use_mock = payload.use_mock or settings.use_mock_data
        fence_info = calculate_fence_info(payload.fence_geojson)
        terrain_metrics, spatial_pattern = analyze_terrain(
            payload.fence_geojson,
            settings.resolved_dem_path,
            use_mock,
        )
        data_status = build_data_status(
            dem_path=settings.resolved_dem_path,
            water_path=settings.resolved_water_path,
            road_path=settings.resolved_road_path,
            use_mock=use_mock,
        )
        water_status = analyze_water_relation(payload.fence_geojson, settings.resolved_water_path)
        data_status["water"].update(water_status)
        spatial_pattern["water_relation"] = water_status["message"]
        scores = calculate_scores(terrain_metrics, spatial_pattern, data_status)
        local_report = generate_report(fence_info, terrain_metrics, spatial_pattern, scores)
        llm_report = generate_llm_report(
            llm_enabled=settings.llm_enabled and not use_mock,
            api_key=settings.llm_api_key,
            base_url=settings.llm_base_url,
            model=settings.llm_model,
            fence_info=fence_info,
            terrain_metrics=terrain_metrics,
            spatial_pattern=spatial_pattern,
            scores=scores,
            data_status=data_status,
            fallback_report=local_report,
        )
        fortune_module = get_fortune_placeholder(scores, terrain_metrics)
        fortune_module["llm_report"] = {
            "enabled": llm_report["enabled"],
            "used": llm_report["used"],
            "provider": llm_report["provider"],
            "model": llm_report.get("model"),
            "message": llm_report["message"],
        }
        return {
            "fence_info": fence_info,
            "terrain_metrics": terrain_metrics,
            "spatial_pattern": spatial_pattern,
            "scores": scores,
            "data_status": data_status,
            "report": llm_report["content"],
            "fortune_module": fortune_module,
            "disclaimer": DISCLAIMER,
        }
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
