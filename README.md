# 山水明堂风水地理信息系统

**Shanshui Mingtang Feng Shui GIS**  
**AI-powered Feng Shui Geospatial Intelligence System**

一个结合 WebGIS、DEM 地形分析、水系空间关系、Cesium 三维视图和 AI 解读的传统环境格局智能评估系统。用户可以在地图上圈画研究区，系统自动汇总海拔、坡度、坡向、地形起伏、河流水系关系等空间指标，并从“靠山、明堂、藏风、得水、纳气、聚财”等传统风水文化视角生成可视化报告。

This project is an AI-assisted WebGIS platform for traditional landscape pattern interpretation. Users can draw a study area on the map, summarize terrain and river metrics, visualize the site in 2D/3D, and generate a Feng Shui cultural interpretation based on structured GIS analysis results.

> 本项目仅用于传统文化研究、环境格局分析与娱乐参考，不构成真实财运预测、投资建议、购房建议、商业选址建议或其他现实决策依据。
>
> This project is for traditional culture research, spatial pattern visualization and entertainment reference only. It does not provide real fortune prediction, investment advice, property advice or business site-selection advice.

## Highlights

- Draw a polygon, rectangle or circle fence directly on a WebGIS map.
- Analyze elevation, slope, aspect, terrain relief and roughness from DEM data.
- Evaluate river/water relation from local vector water datasets.
- Visualize the site with Cesium 3D scene and symbolic spatial markers.
- Generate Feng Shui cultural reports with DeepSeek / OpenAI-compatible LLMs.
- Keep sensitive fence coordinates local; AI receives structured metrics, not raw GeoJSON.
- Support mock mode for quick demos and real-data mode for local geospatial analysis.

## 支持项目与定制分析

如果这个开源项目对你有帮助，欢迎支持作者继续维护和扩展。也欢迎交流定制化 GIS 分析、三维地形可视化、AI 报告生成、私有化部署和数据接入等需求。

前端页面右上角提供 `支持作者 / Support` 弹窗，包含赞赏码：

```text
frontend/public/assets/support.jpg
```

可定制方向包括：

- DEM 高程、坡度、坡向、地形起伏与建设适宜性分析。
- 河流、水系、道路、地块边界等矢量数据接入。
- Cesium 三维地形场景、自有 DEM 地形瓦片和 3D Tiles。
- DeepSeek / OpenAI-compatible AI 风水文化报告生成。
- 私有化部署、云服务器、域名、Nginx 和 Docker 配置。

## 1. 项目简介

本项目是一个“传统环境格局智能评估平台”MVP，结合电子围栏、WebGIS 地图、DEM 地形指标、规则评分和中文报告生成，用于分析用户圈定范围内的山、水、势、向、局、坡度、坡向、高程、开阔度和围合度等环境特征。

第一版默认使用 mock DEM、水系和道路数据，保证系统先跑通；后续可接入真实 GeoTIFF DEM、高精度影像瓦片、Cesium 地形服务、PostGIS 和大语言模型 API。

## 2. 系统定位

- 第一阶段：传统环境格局智能评估平台。
- 后续阶段：风水文化娱乐分析模块，包括命运、财运、吉凶等民俗文化解读入口。
- 娱乐模块必须明确标注为民俗文化娱乐参考，不作为真实人生、投资、医疗、婚姻、法律或商业决策依据。

## 3. 功能模块

- OpenLayers 二维地图：底图切换、Polygon/Rectangle/Circle 电子围栏绘制。
- FastAPI 分析接口：围栏面积、中心点、顶点数、mock 地形指标、规则评分、中文报告。
- Cesium 三维视图：基础三维地球、电子围栏显示、俯视/倾斜/山水格局观察视角。
- ECharts 图表：环境格局评分雷达图。
- 文化娱乐解读：第一版只保留入口和免责声明，不做真实预测。

## 4. 技术栈

- 前端：Vue 3、Vite、OpenLayers、CesiumJS、Axios、ECharts。
- 后端：Python、FastAPI、shapely、pyproj、numpy、pandas、geopandas、rasterio、pydantic、uvicorn。
- 数据：第一版本地 GeoJSON/CSV/DEM 文件预留，不启用数据库。
- 部署：预留 Docker Compose 与 Nginx 反向代理说明。

## 5. 项目结构

```text
backend/                 FastAPI 后端
frontend/                Vue + Vite 前端
docs/                    技术、数据、三维、影像、部署说明
docker-compose.yml       本地容器化预留
```

## 6. 安装前端依赖

```bash
cd frontend
npm install
```

## 7. 安装后端依赖

建议使用虚拟环境：

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

如果 Windows 上安装 `rasterio/geopandas` 较慢，可先使用 mock 模式运行，或改用 conda 安装 GIS 依赖。

## 8. 启动前端

```bash
cd frontend
copy .env.example .env
npm run dev
```

默认访问：`http://127.0.0.1:5173`

## 9. 启动后端

```bash
cd backend
copy .env.example .env
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

健康检查：`http://127.0.0.1:8000/api/health`

## 10. 使用 mock 模式

后端 `.env` 中保持：

```env
USE_MOCK_DATA=true
```

前端提交分析时也默认传 `use_mock: true`。此模式不会读取真实 DEM、水系或道路数据，可以直接返回地形指标、评分和报告。

## 11. 接入真实 DEM 数据

将 GeoTIFF 放入 `backend/data/dem/`，并在 `backend/.env` 中设置：

```env
USE_MOCK_DATA=false
DEM_PATH=./data/dem/your_dem.tif
```

后端已预留 `backend/app/services/terrain_analysis.py` 的真实 DEM 裁剪与坡度坡向计算入口。正式生产建议补充 DEM CRS 检查、nodata 清理、缓冲区邻域采样和方向剖面分析。

## 12. 接入高精度影像底图

在 `frontend/.env` 中配置：

```env
VITE_IMAGERY_TILE_URL=https://your-tile-service/{z}/{x}/{y}.png
```

地图服务 Key 或 Token 不要写死在代码里。若服务商需要鉴权，请通过环境变量或后端代理安全注入。

## 13. 接入 Cesium 三维地形

在 `frontend/.env` 中配置：

```env
VITE_CESIUM_ION_TOKEN=your_token
```

当前组件会在未配置 token 时显示友好提示，并使用基础 mock 三维地球。后续可扩展自有 DEM 切片、3D Tiles、建筑模型和倾斜摄影。

## 14. 后续接入大语言模型 API

后端 `.env` 已预留：

```env
LLM_API_KEY=
LLM_BASE_URL=
LLM_MODEL=
```

第一版报告由 `report_generator.py` 基于结构化 GIS 结果生成，不调用外部模型，也不会上传用户围栏坐标。后续接入 LLM 时，应只传必要的脱敏指标，不上传敏感地块坐标到第三方服务。

## 15. 扩展文化娱乐模块

`backend/app/services/fortune_module.py` 已预留占位函数。第一版返回未开放状态。未来若增加命运、财运、吉凶等内容，必须在前后端同时显示免责声明，并避免绝对化断语。

## 16. 部署到服务器的大致步骤

1. 后端使用 `uvicorn` 或 `gunicorn + uvicorn worker` 运行。
2. 前端执行 `npm run build`，将 `frontend/dist` 交给 Nginx 托管。
3. Nginx 将 `/api/` 反向代理到后端 `127.0.0.1:8000`。
4. `.env` 文件只保存在服务器私有目录，不提交到公开仓库。
5. DEM、影像和矢量数据放在服务器本地安全目录，按权限控制访问。

## 17. 免责声明

本系统基于地理空间数据、DEM地形分析和传统风水文化解释生成报告，仅用于环境格局分析、传统文化研究与娱乐参考，不构成现实人生、投资、医疗、婚姻、法律、商业选址等决策建议。
