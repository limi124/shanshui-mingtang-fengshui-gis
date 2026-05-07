<template>
  <div class="app-shell">
    <header class="topbar">
      <div class="brand-block">
        <div class="brand-mark">山</div>
        <div>
          <h1>风水地理智能分析系统</h1>
          <p>基于高精度影像、DEM三维地形与传统环境格局的智能评估平台</p>
        </div>
      </div>

      <div class="top-search">
        <input placeholder="搜索地点、行政区或坐标" />
        <button>搜索</button>
      </div>

      <div class="top-actions">
        <button @click="loadExampleFence">示例数据</button>
        <button>帮助</button>
        <button class="user-chip">张三</button>
      </div>
    </header>

    <main class="workspace">
      <aside class="side-panel">
        <LayerControl v-model="baseLayer" />

        <DrawToolbar
          :draw-type="drawType"
          :has-fence="Boolean(fenceGeojson)"
          @set-draw-type="drawType = $event"
          @clear="clearFence"
        />

        <section class="panel-section">
          <h2>分析模式</h2>
          <button class="option-row active" @click="analysisMode = 'environment'">环境格局分析</button>
          <button class="option-row" @click="analysisMode = 'terrain'">三维地形分析</button>
          <button class="option-row muted" disabled>
            文化娱乐解读 <span class="locked">后续开放</span>
          </button>
        </section>

        <section class="action-stack">
          <button class="primary-btn" :disabled="!fenceGeojson || loading" @click="startAnalysis">
            {{ loading ? "分析中..." : "开始分析" }}
          </button>
          <button class="secondary-btn" :disabled="!fenceGeojson" @click="showCesium = true">打开三维视图</button>
          <button class="secondary-btn" disabled>导出报告</button>
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
  </div>
</template>

<script setup>
import { ref } from "vue";
import { analyzeFence } from "./api/analysis";
import AnalysisPanel from "./components/AnalysisPanel.vue";
import CesiumView from "./components/CesiumView.vue";
import DrawToolbar from "./components/DrawToolbar.vue";
import LayerControl from "./components/LayerControl.vue";
import MapView from "./components/MapView.vue";

const baseLayer = ref("vector");
const drawType = ref("Polygon");
const analysisMode = ref("environment");
const fenceGeojson = ref(null);
const fenceInfo = ref(null);
const analysisResult = ref(null);
const loading = ref(false);
const showCesium = ref(false);
const mapRef = ref(null);

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
    name: "示例研究区",
  },
};

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
      error: detail || (isTimeout
        ? "分析超时：真实 DEM、水系和 AI 解读耗时较长，请稍后重试，或暂时关闭 LLM_ENABLED。"
        : "分析失败：后端服务可启动但接口返回异常，请查看后端窗口日志。"),
    };
  } finally {
    loading.value = false;
  }
}
</script>
