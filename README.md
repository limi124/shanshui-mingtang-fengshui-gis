# 声明：本项目纯属传统民俗文化娱乐参考；分析精度取决于 Cesium 上传的 DEM 数据集、河流水系数据和本地 GIS 数据质量。欢迎支持项目；有问题可提 Issue，或联系邮箱：lm1248571@gmail.com。

# 山水明堂风水地理信息系统

**Shanshui Mingtang Feng Shui GIS**

![WebGIS](https://img.shields.io/badge/WebGIS-OpenLayers-0f766e)
![3D](https://img.shields.io/badge/3D-CesiumJS-b8860b)
![Backend](https://img.shields.io/badge/Backend-FastAPI-059669)
![AI](https://img.shields.io/badge/AI-DeepSeek-2563eb)
![Culture](https://img.shields.io/badge/Use-Traditional%20Culture%20Entertainment-7c3aed)

**Language:** 中文 | [English](#english)

一个结合 **WebGIS、三维地形、DEM 高程分析、水系空间关系分析和 AI 解读** 的传统环境格局智能评估系统。

用户可以在地图上圈画一个研究区，系统会自动汇总该区域的海拔、高程起伏、坡度、坡向、地形粗糙度、河流水系关系等空间指标，并从传统风水文化中的“靠山、明堂、藏风、得水、纳气、聚财”等视角生成可视化分析结果。

> 注意：本项目不是算命工具，不做真实财运预测，不构成买房、投资、商业选址、医疗、法律、婚姻或人生决策建议。所有风水、聚财、吉凶相关内容均为传统民俗文化娱乐参考。

## 为什么做这个项目

传统风水里经常提到“山、水、势、向、局”，但这些概念如果只靠文字描述，很难直观看到。

这个项目尝试把它们转成可视化和可计算的空间指标：

- “靠山”对应后方地势、相对高差和三维地形背景。
- “明堂”对应前方开阔度、场地舒展度和视域关系。
- “得水”对应河流、水体距离、相交关系和排水风险。
- “藏风”对应左右围合、边界感和风环境象意。
- “纳气、聚财”作为传统民俗文化解释，由 AI 基于本地 GIS 计算结果生成。

AI 不直接凭空判断，而是基于后端计算得到的 DEM、水系、坡向、坡度和评分结果生成报告。

## 功能特点

- OpenLayers 二维地图展示。
- Polygon / Rectangle / Circle 电子围栏绘制。
- DEM 高程、坡度、坡向、地形起伏和粗糙度分析。
- 河流水系关系分析。
- 靠山、明堂、藏风、得水、采光、地形稳定等规则评分。
- Cesium 三维地形视角展示。
- DeepSeek / OpenAI-compatible AI 风水文化解读。
- 聚财格局文化参考报告。
- Mock 模式和真实数据模式切换。
- 敏感围栏坐标默认不发送给 AI，只发送结构化指标。

## 技术栈

**Frontend**

- Vue 3
- Vite
- OpenLayers
- CesiumJS
- Axios
- ECharts

**Backend**

- Python
- FastAPI
- GeoPandas
- Rasterio
- Shapely
- NumPy
- Pandas
- Pydantic
- Uvicorn

## 快速启动

### 1. 安装前端依赖

```bash
cd frontend
npm install
copy .env.example .env
npm run dev
```

默认前端地址：

```text
http://127.0.0.1:5173
```

### 2. 安装后端依赖

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

后端健康检查：

```text
http://127.0.0.1:8000/api/health
```

### 3. 一键启动

Windows 用户可以直接运行：

```bash
start-dev.bat
```

## 配置说明

### 前端 `.env`

```env
VITE_API_BASE_URL=http://127.0.0.1:8000
VITE_CESIUM_ION_TOKEN=
VITE_CESIUM_TERRAIN_ASSET_ID=
VITE_IMAGERY_TILE_URL=
VITE_VECTOR_TILE_URL=
VITE_USE_MOCK_DATA=false
```

### 后端 `.env`

```env
APP_NAME=Fengshui GIS
DEBUG=true
USE_MOCK_DATA=true
DEM_PATH=./data/dem/sample_dem.tif
VECTOR_WATER_PATH=./data/vector/water.geojson
VECTOR_ROAD_PATH=./data/vector/road.geojson
LLM_ENABLED=false
LLM_API_KEY=
LLM_BASE_URL=
LLM_MODEL=
```

## 接入真实数据

### DEM 数据

将 GeoTIFF DEM 放入本地数据目录，并在 `backend/.env` 配置：

```env
USE_MOCK_DATA=false
DEM_PATH=./data/dem/your_dem.tif
```

三维地形精度取决于你上传到 Cesium ion 或自有地形服务的 DEM 数据集质量、分辨率和切片方式。

### 水系数据

可使用 GeoJSON 或 Shapefile 格式的河流、水体数据：

```env
VECTOR_WATER_PATH=./data/vector/water.geojson
```

后端会根据电子围栏计算水系关系，例如是否相交、最近距离、方位和得水评分。

### AI 解读

支持 DeepSeek 或其他 OpenAI-compatible API：

```env
LLM_ENABLED=true
LLM_BASE_URL=https://api.deepseek.com
LLM_MODEL=deepseek-v4-flash
LLM_API_KEY=your_api_key
```

安全说明：后端只向 AI 发送面积、坡度、坡向、水系关系、评分等结构化指标，不发送原始电子围栏 GeoJSON 坐标。

## 支持项目与定制分析

如果这个开源项目对你有帮助，欢迎支持作者继续维护和扩展。

前端页面右上角提供 `支持作者 / Support` 弹窗，包含赞赏码：

```text
frontend/public/assets/support.jpg
```

也欢迎交流定制分析和开发需求：

- DEM 高程、坡度、坡向、地形起伏分析。
- 河流、水系、道路、地块边界等矢量数据接入。
- Cesium 三维地形、自有 DEM 地形瓦片和 3D Tiles。
- DeepSeek / OpenAI-compatible AI 报告生成。
- 私有化部署、服务器、域名、Nginx 和 Docker 配置。

有问题可以：

- 提交 GitHub Issue。
- 发送邮件：`lm1248571@gmail.com`。

## 项目结构

```text
backend/                 FastAPI backend
frontend/                Vue + Vite frontend
docs/                    Technical and deployment docs
scripts/                 One-click startup scripts
docker-compose.yml       Docker Compose placeholder
start-dev.bat            One-click local startup
```

## 免责声明

本系统基于地理空间数据、DEM 地形分析和传统风水文化解释生成报告，仅用于环境格局分析、传统文化研究与娱乐参考，不构成现实人生、投资、医疗、婚姻、法律、商业选址等决策建议。

---

<a id="english"></a>

# Shanshui Mingtang Feng Shui GIS

**Statement: This project is for traditional folk culture entertainment only. The analysis quality depends on the Cesium-uploaded DEM dataset, river data and local GIS data quality. Support is welcome. For questions, please open an Issue or contact: lm1248571@gmail.com.**

**Language:** [中文](#山水明堂风水地理信息系统) | English

Shanshui Mingtang Feng Shui GIS is an AI-assisted WebGIS platform for traditional landscape pattern interpretation.

Users can draw a study area on the map, summarize elevation, slope, aspect, terrain relief, roughness and river-water relations, then generate a cultural Feng Shui interpretation based on structured GIS analysis results.

This project focuses on visualizing traditional concepts such as mountain backing, Mingtang openness, wind enclosure, water relation, Qi intake and wealth symbolism. It does not provide real fortune prediction or decision-making advice.

## Core Features

- Draw polygon, rectangle or circle fences on a WebGIS map.
- Analyze DEM elevation, slope, aspect, terrain relief and roughness.
- Evaluate river and water-body relations from local vector data.
- Visualize symbolic terrain patterns in Cesium 3D.
- Generate cultural reports with DeepSeek or OpenAI-compatible LLMs.
- Keep sensitive fence coordinates local by sending only structured metrics to AI.

## Quick Start

```bash
cd frontend
npm install
copy .env.example .env
npm run dev
```

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

Or run:

```bash
start-dev.bat
```

## Support and Custom Work

If this project is useful or inspiring, support is welcome. The frontend includes a `Support` modal with the donation QR code at:

```text
frontend/public/assets/support.jpg
```

Custom GIS analysis, Cesium 3D scenes, AI report generation, private deployment and data integration are welcome.

Contact: `lm1248571@gmail.com`

## Disclaimer

This project is for traditional culture research, landscape pattern visualization and entertainment reference only. It does not provide real fortune prediction, investment advice, property advice, medical advice, legal advice or business site-selection advice.
