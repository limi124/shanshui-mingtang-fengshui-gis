import axios from "axios";

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000",
  // Real DEM + water analysis + AI interpretation can take 30-60 seconds.
  timeout: 90000,
});

export function analyzeFence(fenceGeojson, analysisMode = "environment") {
  const useMock = import.meta.env.VITE_USE_MOCK_DATA === "true";
  return api.post("/api/analysis/fence", {
    fence_geojson: fenceGeojson,
    analysis_mode: analysisMode,
    use_mock: useMock,
  });
}

export function getSceneConfig() {
  return api.get("/api/map/scene-config");
}
