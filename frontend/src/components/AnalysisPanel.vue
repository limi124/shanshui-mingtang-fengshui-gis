<template>
  <aside class="result-panel">
    <div class="result-heading">
      <h2>分析结果</h2>
      <button :disabled="!result || result.error || loading" @click="$emit('reanalyze')">
        {{ loading ? "分析中" : "重新分析" }}
      </button>
    </div>

    <div class="result-tabs">
      <button :class="{ active: activeTab === 'score' }" @click="activeTab = 'score'">综合评分</button>
      <button :class="{ active: activeTab === 'terrain' }" @click="activeTab = 'terrain'">指标说明</button>
      <button :class="{ active: activeTab === 'advice' }" @click="activeTab = 'advice'">居住建议</button>
      <button :class="{ active: activeTab === 'wealth' }" @click="activeTab = 'wealth'">聚财格局</button>
      <button :class="{ active: activeTab === 'report' }" @click="activeTab = 'report'">完整报告</button>
    </div>

    <div v-if="loading" class="loading-box">正在基于电子围栏计算地形指标、空间格局与规则评分...</div>
    <div v-else-if="result?.error" class="error-box">{{ result.error }}</div>

    <template v-else-if="result">
      <section v-if="activeTab === 'score'" class="tab-body">
        <section class="score-hero">
          <div>
            <span>综合风水评分</span>
            <strong>{{ result.scores.overall_score }}<small>分</small></strong>
            <p>{{ scoreLevel }}</p>
          </div>
          <div class="compass-card">
            <div class="compass-ring"></div>
            <div class="compass-mountain"></div>
          </div>
        </section>

        <div class="metric-grid">
          <Metric label="平均高程" :value="`${result.terrain_metrics.mean_elevation} m`" tone="场地海拔背景" />
          <Metric label="平均坡度" :value="`${result.terrain_metrics.mean_slope}°`" tone="建设舒适度" />
          <Metric label="主要坡向" :value="result.terrain_metrics.dominant_aspect" tone="采光通风" />
          <Metric label="围栏面积" :value="`${areaKm2} km²`" tone="已圈定" />
          <Metric label="得水生财" :value="`${result.scores.water_score} 分`" :tone="waterScoreTone" />
          <Metric label="数据状态" :value="waterStatusLabel" tone="水系图层" />
        </div>

        <ScoreChart :scores="result.scores" />
        <section v-if="waterStatusMessage" class="disclaimer">{{ waterStatusMessage }}</section>
      </section>

      <section v-if="activeTab === 'terrain'" class="tab-body terrain-list">
        <h3>地形指标与意义</h3>
        <div v-for="item in terrainRows" :key="item.label" class="info-row info-row-rich">
          <div>
            <span>{{ item.label }}</span>
            <p>{{ item.note }}</p>
          </div>
          <strong>{{ item.value }}</strong>
        </div>
      </section>

      <section v-if="activeTab === 'advice'" class="tab-body">
        <section class="ai-summary">
          <h3>这个房子/地块的人应该怎么做</h3>
          <ul class="advice-list">
            <li v-for="item in recommendations" :key="item">{{ item }}</li>
          </ul>
        </section>
        <section class="ai-summary">
          <h3>现代地理风险提示</h3>
          <p>{{ riskText }}</p>
        </section>
      </section>

      <section v-if="activeTab === 'wealth'" class="tab-body">
        <section class="score-hero wealth-hero">
          <div>
            <span>{{ wealthReference.title || "民俗聚财格局" }}</span>
            <strong>{{ wealthReference.wealth_culture_score || "--" }}<small>分</small></strong>
            <p>{{ wealthLevel }}</p>
          </div>
          <div class="compass-card">
            <div class="compass-ring"></div>
            <div class="compass-mountain"></div>
          </div>
        </section>
        <section class="ai-summary">
          <h3>纳气聚财文化解读</h3>
          <p>{{ wealthReference.tendency }}</p>
          <div class="wealth-detail-list">
            <div v-for="item in wealthInterpretation" :key="item.title" class="wealth-detail">
              <strong>{{ item.title }}</strong>
              <p>{{ item.content }}</p>
            </div>
          </div>
        </section>
        <section class="ai-summary">
          <h3>提升聚财观感的环境整理</h3>
          <ul class="advice-list">
            <li v-for="item in wealthReference.actions || []" :key="item">{{ item }}</li>
          </ul>
        </section>
        <section class="disclaimer">{{ wealthReference.disclaimer || result.disclaimer }}</section>
      </section>

      <section v-if="activeTab === 'report'" class="tab-body">
        <section class="ai-summary">
          <h3>AI解读摘要</h3>
          <p class="source-line">{{ llmStatusText }}</p>
          <p>{{ summary }}</p>
        </section>
        <section class="report-block report-block-large">
          <h3>完整报告</h3>
          <p>{{ result.report }}</p>
        </section>
      </section>
    </template>

    <template v-else>
      <section class="score-hero muted-card">
        <div>
          <span>综合风水评分</span>
          <strong>--<small>分</small></strong>
          <p>请先绘制电子围栏并开始分析</p>
        </div>
        <div class="compass-card">
          <div class="compass-ring"></div>
          <div class="compass-mountain"></div>
        </div>
      </section>
      <div class="empty-state">
        <p>点击“示例数据”可快速载入演示围栏；也可以手动绘制多边形、矩形或圆形电子围栏。</p>
        <p v-if="fenceInfo">当前围栏面积约 {{ fenceInfo.area_m2.toLocaleString() }} m²。</p>
      </div>
    </template>
  </aside>
</template>

<script setup>
import { computed, ref } from "vue";
import ScoreChart from "./ScoreChart.vue";

const props = defineProps({
  result: {
    type: Object,
    default: null,
  },
  fenceInfo: {
    type: Object,
    default: null,
  },
  loading: {
    type: Boolean,
    default: false,
  },
});

defineEmits(["reanalyze"]);

const activeTab = ref("score");

const areaKm2 = computed(() => {
  if (!props.result) return "--";
  return (props.result.fence_info.area_m2 / 1_000_000).toFixed(2);
});

const metricExplanations = computed(() => props.result?.fortune_module?.metric_explanations || {});
const recommendations = computed(() => props.result?.fortune_module?.living_recommendations || []);
const wealthReference = computed(() => props.result?.fortune_module?.wealth_reference || {});
const wealthInterpretation = computed(() => wealthReference.value?.interpretation || []);
const waterStatus = computed(() => props.result?.data_status?.water || {});
const llmReport = computed(() => props.result?.fortune_module?.llm_report || {});

const llmStatusText = computed(() => {
  if (llmReport.value.used) return `已调用 AI 模型 ${llmReport.value.model || ""}，基于本地 GIS 指标生成解读。`;
  return llmReport.value.message || "当前使用本地模板报告。";
});

const terrainRows = computed(() => {
  if (!props.result) return [];
  const terrain = props.result.terrain_metrics;
  return [
    { label: "平均高程", value: `${terrain.mean_elevation} m`, note: explain("mean_elevation") },
    { label: "最高高程", value: `${terrain.max_elevation} m`, note: "用于判断范围内最高地形位置，辅助识别可能的背靠或高点。" },
    { label: "最低高程", value: `${terrain.min_elevation} m`, note: "用于识别低洼区域，后续需结合排水与积水风险判断。" },
    { label: "相对高差", value: `${terrain.relief} m`, note: explain("relief") },
    { label: "平均坡度", value: `${terrain.mean_slope}°`, note: explain("mean_slope") },
    { label: "最大坡度", value: `${terrain.max_slope}°`, note: "用于识别陡坡或边坡风险，建设前需重点核验。" },
    { label: "主要坡向", value: terrain.dominant_aspect, note: explain("dominant_aspect") },
    { label: "地形粗糙度", value: terrain.terrain_roughness, note: explain("terrain_roughness") },
    { label: "得水条件评分", value: `${props.result.scores.water_score} 分`, note: waterMetricNote.value },
  ];
});

const waterStatusLabel = computed(() => {
  if (!props.result) return "--";
  if (waterStatus.value.status === "missing") return "待接入";
  if (waterStatus.value.status === "pending_integration") return "待启用";
  return "已接入";
});

const waterScoreTone = computed(() => {
  if (waterStatus.value.is_placeholder) return "中性占位";
  return "真实水系";
});

const waterStatusMessage = computed(() => waterStatus.value.message || "");

const waterMetricNote = computed(() => {
  if (waterStatus.value.is_placeholder) {
    return "当前未启用真实水系空间计算，60 分为中性占位分，并已从综合评分确定性计算中排除。后续接入 water.geojson 后，可计算最近水体距离、方位、穿越关系与汇水风险。";
  }
  return "该指标基于本地水系数据计算，用于描述水体距离、方位、汇水与排水关系。从传统文化语境看，可作为“得水生财”的象意参考；现实层面仍需核验洪水位、退让红线和排水安全。";
});

const scoreLevel = computed(() => {
  const score = props.result?.scores?.overall_score || 0;
  if (score >= 85) return "优";
  if (score >= 70) return "良";
  return "待优化";
});

const wealthLevel = computed(() => {
  const score = wealthReference.value?.wealth_culture_score || 0;
  if (score >= 80) return "明堂纳气，聚财象意较强";
  if (score >= 65) return "具备一定纳气聚财基础";
  return "宜先整理明堂、水路与入口";
});

const summary = computed(() => {
  if (!props.result) return "";
  const terrain = props.result.terrain_metrics;
  return `该区域地势为${terrain.terrain_position}，主要坡向${terrain.dominant_aspect}，平均坡度${terrain.mean_slope}°。从传统风水文化视角看，可重点关注“靠山是否稳、明堂是否开、水路是否清、左右是否藏风”；从现代地理视角看，应同步复核真实DEM、水系和排水风险。`;
});

const riskText = computed(() => {
  if (!props.result) return "";
  const terrain = props.result.terrain_metrics;
  const notes = [];
  if (terrain.mean_slope > 15) notes.push("平均坡度偏大，建议复核边坡稳定性。");
  if (terrain.relief > 150) notes.push("相对高差较大，建议补充地形剖面与排水分析。");
  if (notes.length === 0) notes.push("当前 mock 指标显示坡度适中，但正式结论仍需真实 DEM 与现场核验。");
  return notes.join(" ");
});

function explain(key) {
  return metricExplanations.value[key] || "该指标用于辅助理解场地空间环境，正式结论需结合真实数据和现场核验。";
}

const Metric = {
  props: ["label", "value", "tone"],
  template: `<div class="metric-card"><span>{{ label }}</span><strong>{{ value }}</strong><em>{{ tone }}</em></div>`,
};

</script>
