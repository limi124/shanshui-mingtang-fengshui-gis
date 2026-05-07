from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.routers.analysis import router as analysis_router


app = FastAPI(title=settings.app_name, debug=settings.debug)

# 前端本地开发默认端口为 5173，生产环境可在 Nginx 中收紧 CORS。
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health_check():
    return {"status": "ok", "message": "fengshui gis backend is running"}


@app.get("/api/map/scene-config")
def scene_config():
    return {
        "imagery_provider": "mock",
        "terrain_provider": "mock",
        "cesium_token_required": True,
        "message": "请在前端 .env 中配置 VITE_CESIUM_ION_TOKEN",
    }


app.include_router(analysis_router, prefix="/api/analysis", tags=["analysis"])
