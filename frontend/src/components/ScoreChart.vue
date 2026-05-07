<template>
  <div class="chart-box">
    <div class="chart-title">指标雷达图</div>
    <div ref="chartEl" class="score-chart"></div>
  </div>
</template>

<script setup>
import * as echarts from "echarts";
import { onBeforeUnmount, onMounted, ref, watch } from "vue";

const props = defineProps({
  scores: {
    type: Object,
    required: true,
  },
});

const chartEl = ref(null);
let chart;

onMounted(() => {
  chart = echarts.init(chartEl.value, "dark");
  renderChart();
  window.addEventListener("resize", resizeChart);
});

onBeforeUnmount(() => {
  window.removeEventListener("resize", resizeChart);
  chart?.dispose();
});

watch(() => props.scores, renderChart, { deep: true });

function resizeChart() {
  chart?.resize();
}

function renderChart() {
  if (!chart) return;
  chart.setOption({
    backgroundColor: "transparent",
    tooltip: {},
    radar: {
      radius: "62%",
      axisName: { color: "#cfeee4", fontSize: 11 },
      splitLine: { lineStyle: { color: "rgba(92, 209, 174, 0.25)" } },
      splitArea: { areaStyle: { color: ["rgba(22, 128, 105, 0.16)", "rgba(22, 128, 105, 0.04)"] } },
      axisLine: { lineStyle: { color: "rgba(92, 209, 174, 0.35)" } },
      indicator: [
        { name: "地势形态", max: 100 },
        { name: "水文条件", max: 100 },
        { name: "视域开阔", max: 100 },
        { name: "环境宜居", max: 100 },
        { name: "交通可达", max: 100 },
        { name: "生态环境", max: 100 },
      ],
    },
    series: [
      {
        type: "radar",
        symbolSize: 4,
        lineStyle: { color: "#2bd6a0", width: 2 },
        areaStyle: { color: "rgba(43, 214, 160, 0.38)" },
        itemStyle: { color: "#f0d58a" },
        data: [
          {
            value: [
              props.scores.back_mountain_score,
              props.scores.water_score,
              props.scores.front_open_score,
              props.scores.terrain_stability_score,
              props.scores.enclosure_score,
              props.scores.aspect_light_score,
            ],
            name: "本区域",
          },
        ],
      },
    ],
  });
}
</script>
