<template>
  <div class="app-shell">
    <header class="topbar premium-topbar">
      <div class="brand-block">
        <div class="brand-mark">山</div>
        <div>
          <h1>{{ t.title }}</h1>
          <p>{{ t.subtitle }}</p>
        </div>
      </div>

      <div class="top-search">
        <input :placeholder="t.searchPlaceholder" />
        <button>{{ t.search }}</button>
      </div>

      <div class="top-actions">
        <button @click="loadExampleFence">{{ t.sample }}</button>
        <button @click="showConfigGuide = true">{{ t.config }}</button>
        <button @click="showSupport = true">{{ t.support }}</button>
        <button class="lang-toggle" @click="toggleLanguage">{{ t.langSwitch }}</button>
      </div>
    </header>

    <main class="workspace premium-workspace">
      <aside class="side-panel premium-side-panel">
        <section class="project-card">
          <span>{{ t.projectTag }}</span>
          <strong>{{ t.projectName }}</strong>
          <p>{{ t.projectIntro }}</p>
        </section>

        <LayerControl v-model="baseLayer" :labels="t.layerControl" />

        <DrawToolbar
          :draw-type="drawType"
          :has-fence="Boolean(fenceGeojson)"
          :labels="t.drawToolbar"
          @set-draw-type="drawType = $event"
          @clear="clearFence"
        />

        <section class="panel-section">
          <h2>{{ t.analysisMode.title }}</h2>
          <button class="option-row active" @click="analysisMode = 'environment'">{{ t.analysisMode.environment }}</button>
          <button class="option-row" @click="analysisMode = 'terrain'">{{ t.analysisMode.terrain }}</button>
          <button class="option-row muted" disabled>
            {{ t.analysisMode.culture }} <span class="locked">{{ t.analysisMode.locked }}</span>
          </button>
        </section>

        <section class="action-stack">
          <button class="primary-btn" :disabled="!fenceGeojson || loading" @click="startAnalysis">
            {{ loading ? t.analyzing : t.startAnalysis }}
          </button>
          <button class="secondary-btn" :disabled="!fenceGeojson" @click="showCesium = true">{{ t.open3d }}</button>
          <button class="secondary-btn" disabled>{{ t.exportReport }}</button>
        </section>
      </aside>

      <section class="map-stage">
        <MapView
          ref="mapRef"
          :base-layer="baseLayer"
          :draw-type="drawType"
          :fence-ready="Boolean(fenceGeojson)"
          :analysis-result="analysisResult"
          @fence-created="handleFenceCreated"
          @fence-cleared="handleFenceCleared"
          @open-cesium="showCesium = true"
        />
      </section>

      <AnalysisPanel
        :result="analysisResult"
        :fence-info="fenceInfo"
        :loading="loading"
        @reanalyze="startAnalysis"
      />
    </main>

    <CesiumView
      v-if="showCesium"
      :fence-geojson="fenceGeojson"
      @close="showCesium = false"
    />

    <div v-if="showConfigGuide" class="modal-backdrop" @click.self="showConfigGuide = false">
      <section class="config-modal">
        <div class="modal-heading">
          <div>
            <p class="eyebrow">{{ t.configGuide.eyebrow }}</p>
            <h2>{{ t.configGuide.title }}</h2>
          </div>
          <button @click="showConfigGuide = false">{{ t.configGuide.close }}</button>
        </div>

        <div class="config-grid">
          <article v-for="item in t.configGuide.steps" :key="item.title" class="config-step">
            <span>{{ item.index }}</span>
            <h3>{{ item.title }}</h3>
            <p>{{ item.copy }}</p>
            <pre v-if="item.code"><code>{{ item.code }}</code></pre>
          </article>
        </div>

        <p class="config-note">{{ t.configGuide.note }}</p>
      </section>
    </div>

    <div v-if="showSupport" class="modal-backdrop" @click.self="showSupport = false">
      <section class="support-modal">
        <div class="modal-heading">
          <div>
            <p class="eyebrow">{{ t.supportModal.eyebrow }}</p>
            <h2>{{ t.supportModal.title }}</h2>
          </div>
          <button @click="showSupport = false">{{ t.supportModal.close }}</button>
        </div>

        <div class="support-content">
          <div class="support-copy">
            <p>{{ t.supportModal.copy }}</p>
            <ul>
              <li v-for="item in t.supportModal.items" :key="item">{{ item }}</li>
            </ul>
            <p class="config-note">{{ t.supportModal.note }}</p>
          </div>
          <div class="qr-card">
            <img src="/assets/support.jpg" :alt="t.supportModal.qrAlt" />
            <span>{{ t.supportModal.qrCaption }}</span>
          </div>
        </div>
      </section>
    </div>
  </div>
</template>

<script setup>
import { computed, ref } from "vue";
import { analyzeFence } from "./api/analysis";
import AnalysisPanel from "./components/AnalysisPanel.vue";
import CesiumView from "./components/CesiumView.vue";
import DrawToolbar from "./components/DrawToolbar.vue";
import LayerControl from "./components/LayerControl.vue";
import MapView from "./components/MapView.vue";

const language = ref("zh");
const baseLayer = ref("vector");
const drawType = ref("Polygon");
const analysisMode = ref("environment");
const fenceGeojson = ref(null);
const fenceInfo = ref(null);
const analysisResult = ref(null);
const loading = ref(false);
const showCesium = ref(false);
const showConfigGuide = ref(false);
const showSupport = ref(false);
const mapRef = ref(null);

const messages = {
  en: {
    title: "Shanshui Mingtang Feng Shui GIS",
    subtitle: "A 2D/3D WebGIS platform for terrain, water, aspect and traditional spatial pattern interpretation.",
    searchPlaceholder: "Search place, district or coordinates",
    search: "Search",
    sample: "Sample Area",
    config: "Configuration",
    support: "Support",
    langSwitch: "中文",
    projectTag: "Open-source MVP",
    projectName: "Draw a site, read the landscape",
    projectIntro: "Fence an area, summarize DEM and river metrics, then let AI explain mountain, water, Mingtang and wealth symbolism.",
    layerControl: {
      title: "Basemap",
      vector: "Vector Map",
      imagery: "Imagery",
      terrain: "Terrain Shade",
    },
    drawToolbar: {
      title: "Draw Tools",
      polygon: "Polygon",
      rectangle: "Rectangle",
      circle: "Circle",
      clear: "Clear",
    },
    analysisMode: {
      title: "Analysis Mode",
      environment: "Environmental Pattern",
      terrain: "3D Terrain Review",
      culture: "Cultural Reading",
      locked: "Coming soon",
    },
    startAnalysis: "Start Analysis",
    analyzing: "Analyzing...",
    open3d: "Open 3D Scene",
    exportReport: "Export Report",
    errors: {
      timeout: "Analysis timed out. Real DEM, river data and AI interpretation may take longer. Try again later or disable LLM_ENABLED.",
      failed: "Analysis failed. The backend may be running, but the API returned an error. Please check backend logs.",
    },
    configGuide: {
      eyebrow: "Setup guide",
      title: "Configuration Tutorial",
      close: "Close",
      steps: [
        {
          index: "01",
          title: "Create frontend env",
          copy: "Copy the example file and fill in your Cesium token only on your local machine. Never commit .env.",
          code: "cd frontend\ncopy .env.example .env\nVITE_CESIUM_ION_TOKEN=your_cesium_token\nVITE_CESIUM_TERRAIN_ASSET_ID=your_terrain_asset_id",
        },
        {
          index: "02",
          title: "Create backend env",
          copy: "Use mock mode first. When real DEM and river data are ready, set USE_MOCK_DATA=false and point paths to local files.",
          code: "cd backend\ncopy .env.example .env\nUSE_MOCK_DATA=true\nDEM_PATH=./data/dem/sample_dem.tif\nVECTOR_WATER_PATH=./data/vector/water.geojson",
        },
        {
          index: "03",
          title: "Enable AI interpretation",
          copy: "Use any OpenAI-compatible provider such as DeepSeek. The backend sends structured metrics, not raw fence coordinates.",
          code: "LLM_ENABLED=true\nLLM_BASE_URL=https://api.deepseek.com\nLLM_MODEL=deepseek-v4-flash\nLLM_API_KEY=your_api_key",
        },
        {
          index: "04",
          title: "Run the system",
          copy: "Start both frontend and backend with the one-click script, then open the local Vite URL.",
          code: "start-dev.bat\n# Frontend: http://127.0.0.1:5173\n# Backend:  http://127.0.0.1:8000",
        },
      ],
      note: "Security note: .env, local DEM, Shapefile, dist and node_modules are ignored by Git. Keep all keys and private geospatial data local.",
    },
    supportModal: {
      eyebrow: "Open-source support",
      title: "Support Shanshui Mingtang",
      close: "Close",
      copy: "If this WebGIS Feng Shui project is useful or inspiring to you, support is warmly appreciated. Custom geospatial analysis and deployment consulting are also welcome.",
      items: [
        "Custom DEM, river and terrain analysis workflows",
        "Cesium 3D terrain scene customization",
        "AI report prompt and local data integration",
        "Private deployment and domain setup assistance",
      ],
      note: "This project is for traditional culture research and entertainment reference. Custom work can focus on GIS, data visualization and AI report generation.",
      qrAlt: "Support QR code",
      qrCaption: "Scan to support the open-source project",
    },
  },
  zh: {
    title: "山水明堂风水地理信息系统",
    subtitle: "面向地形、水系、坡向与传统空间格局解读的二维/三维 WebGIS 平台。",
    searchPlaceholder: "搜索地点、行政区或坐标",
    search: "搜索",
    sample: "示例数据",
    config: "配置教程",
    support: "支持作者",
    langSwitch: "EN",
    projectTag: "开源 MVP",
    projectName: "圈一块地，读懂山水格局",
    projectIntro: "绘制研究区后，系统汇总 DEM 与河流指标，再由 AI 解读靠山、明堂、得水与聚财象意。",
    layerControl: {
      title: "底图切换",
      vector: "矢量底图",
      imagery: "影像底图",
      terrain: "地形阴影",
    },
    drawToolbar: {
      title: "绘制工具",
      polygon: "多边形",
      rectangle: "矩形",
      circle: "圆形",
      clear: "清除",
    },
    analysisMode: {
      title: "分析模式",
      environment: "环境格局分析",
      terrain: "三维地形分析",
      culture: "文化娱乐解读",
      locked: "后续开放",
    },
    startAnalysis: "开始分析",
    analyzing: "分析中...",
    open3d: "打开三维视图",
    exportReport: "导出报告",
    errors: {
      timeout: "分析超时：真实 DEM、水系和 AI 解读耗时较长，请稍后重试，或暂时关闭 LLM_ENABLED。",
      failed: "分析失败：后端服务可启动但接口返回异常，请查看后端窗口日志。",
    },
    configGuide: {
      eyebrow: "快速上手",
      title: "配置教程",
      close: "关闭",
      steps: [
        {
          index: "01",
          title: "配置前端环境",
          copy: "复制示例配置，只在本地填写 Cesium token。不要提交 .env。",
          code: "cd frontend\ncopy .env.example .env\nVITE_CESIUM_ION_TOKEN=你的_cesium_token\nVITE_CESIUM_TERRAIN_ASSET_ID=你的_terrain_asset_id",
        },
        {
          index: "02",
          title: "配置后端环境",
          copy: "先用 mock 模式跑通。准备好真实 DEM 和水系数据后，再改成真实数据路径。",
          code: "cd backend\ncopy .env.example .env\nUSE_MOCK_DATA=true\nDEM_PATH=./data/dem/sample_dem.tif\nVECTOR_WATER_PATH=./data/vector/water.geojson",
        },
        {
          index: "03",
          title: "开启 AI 解读",
          copy: "支持 DeepSeek 等 OpenAI 兼容接口。后端只发送结构化指标，不发送原始围栏坐标。",
          code: "LLM_ENABLED=true\nLLM_BASE_URL=https://api.deepseek.com\nLLM_MODEL=deepseek-v4-flash\nLLM_API_KEY=你的_api_key",
        },
        {
          index: "04",
          title: "一键启动",
          copy: "使用一键脚本同时启动前后端，然后打开本地 Vite 地址。",
          code: "start-dev.bat\n# 前端: http://127.0.0.1:5173\n# 后端: http://127.0.0.1:8000",
        },
      ],
      note: "安全提示：.env、本地 DEM、Shapefile、dist 和 node_modules 已被 Git 忽略。请把密钥和私有地理数据留在本地。",
    },
    supportModal: {
      eyebrow: "开源支持",
      title: "支持山水明堂",
      close: "关闭",
      copy: "如果这个风水地理信息系统对你有启发，欢迎赞赏支持。也欢迎交流定制分析、私有部署和 GIS 可视化开发。",
      items: [
        "定制 DEM、河流、水系与地形分析流程",
        "Cesium 三维地形场景定制",
        "AI 报告提示词与本地数据接入",
        "私有化部署、服务器和域名配置协助",
      ],
      note: "本项目用于传统文化研究与娱乐参考。定制服务主要面向 GIS 分析、数据可视化和 AI 报告生成。",
      qrAlt: "赞赏码",
      qrCaption: "扫码支持开源项目",
    },
  },
};

const t = computed(() => messages[language.value]);

const exampleFence = {
  type: "Feature",
  geometry: {
    type: "Polygon",
    coordinates: [[
      [114.925, 25.826],
      [114.935, 25.848],
      [114.956, 25.854],
      [114.972, 25.842],
      [114.967, 25.818],
      [114.943, 25.809],
      [114.924, 25.818],
      [114.925, 25.826],
    ]],
  },
  properties: {
    name: "Sample Study Area",
  },
};

function toggleLanguage() {
  language.value = language.value === "en" ? "zh" : "en";
}

function handleFenceCreated(payload) {
  fenceGeojson.value = payload.geojson;
  fenceInfo.value = payload.info;
  analysisResult.value = null;
}

function handleFenceCleared() {
  fenceGeojson.value = null;
  fenceInfo.value = null;
  analysisResult.value = null;
}

function clearFence() {
  mapRef.value?.clearFence();
}

function loadExampleFence() {
  mapRef.value?.setFenceGeojson(exampleFence);
}

async function startAnalysis() {
  if (!fenceGeojson.value || loading.value) return;
  loading.value = true;
  try {
    const { data } = await analyzeFence(fenceGeojson.value, analysisMode.value);
    analysisResult.value = data;
  } catch (error) {
    const isTimeout = error?.code === "ECONNABORTED";
    const detail = error?.response?.data?.detail;
    analysisResult.value = {
      error: detail || (isTimeout ? t.value.errors.timeout : t.value.errors.failed),
    };
  } finally {
    loading.value = false;
  }
}
</script>
