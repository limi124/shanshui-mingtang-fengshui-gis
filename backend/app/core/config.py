from functools import lru_cache
from pathlib import Path

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Fengshui GIS"
    debug: bool = True
    use_mock_data: bool = True
    dem_path: str = "./data/dem/sample_dem.tif"
    vector_water_path: str = "./data/vector/water.geojson"
    vector_road_path: str = "./data/vector/road.geojson"
    llm_enabled: bool = False
    llm_api_key: str = ""
    llm_base_url: str = ""
    llm_model: str = ""
    cors_origins: list[str] = ["http://127.0.0.1:5173", "http://localhost:5173"]

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    @field_validator("debug", mode="before")
    @classmethod
    def parse_debug(cls, value):
        if isinstance(value, str) and value.lower() in {"release", "prod", "production"}:
            return False
        return value

    @property
    def resolved_dem_path(self) -> Path:
        return Path(self.dem_path)

    @property
    def resolved_water_path(self) -> Path:
        return Path(self.vector_water_path)

    @property
    def resolved_road_path(self) -> Path:
        return Path(self.vector_road_path)


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
