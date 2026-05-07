<template>
  <div class="map-wrapper">
    <div class="map-toolbar">
      <button>定位/搜索</button>
      <button>比例尺 1:50,000</button>
      <button>坐标 {{ displayCoordinate }}</button>
      <div class="mode-toggle">
        <button class="active">2D</button>
        <button :disabled="!fenceReady" @click="$emit('open-cesium')">3D</button>
      </div>
    </div>

    <div ref="mapEl" class="ol-map"></div>

    <div v-if="fenceInfo" class="map-readout">
      <span>当前选择</span>
      <strong>用户圈定范围</strong>
      <p>围栏面积：{{ fenceInfo.area_m2.toLocaleString() }} m²</p>
      <p>中心点：{{ fenceInfo.center_lon }}, {{ fenceInfo.center_lat }}</p>
      <button @click="$emit('open-cesium')">查看三维格局</button>
    </div>

    <div class="coordinate-bar">
      经度 {{ displayCoordinate.split(",")[0] }}　纬度 {{ displayCoordinate.split(",")[1] || "25.836000" }}
    </div>
  </div>
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, ref, watch } from "vue";
import Map from "ol/Map";
import View from "ol/View";
import Feature from "ol/Feature";
import GeoJSON from "ol/format/GeoJSON";
import { Circle as CircleGeom, Point, Polygon } from "ol/geom";
import { Draw } from "ol/interaction";
import { createBox } from "ol/interaction/Draw";
import TileLayer from "ol/layer/Tile";
import VectorLayer from "ol/layer/Vector";
import OSM from "ol/source/OSM";
import XYZ from "ol/source/XYZ";
import VectorSource from "ol/source/Vector";
import { Fill, Stroke, Style, Circle as CircleStyle, Text } from "ol/style";
import { fromLonLat, toLonLat } from "ol/proj";
import { getArea } from "ol/sphere";

const props = defineProps({
  baseLayer: {
    type: String,
    required: true,
  },
  drawType: {
    type: String,
    required: true,
  },
  fenceReady: {
    type: Boolean,
    default: false,
  },
  analysisResult: {
    type: Object,
    default: null,
  },
});

const emit = defineEmits(["fence-created", "fence-cleared", "open-cesium"]);
const mapEl = ref(null);
const fenceInfo = ref(null);
const pointerLonLat = ref([114.94, 25.836]);
let map;
let drawInteraction;
let currentFenceFeature = null;

const displayCoordinate = computed(() => `${pointerLonLat.value[0].toFixed(6)}, ${pointerLonLat.value[1].toFixed(6)}`);

const vectorSource = new VectorSource();
const markerSource = new VectorSource();

const fenceLayer = new VectorLayer({
  source: vectorSource,
  style: new Style({
    stroke: new Stroke({ color: "#22c58f", width: 3 }),
    fill: new Fill({ color: "rgba(59, 198, 142, 0.25)" }),
    image: new CircleStyle({
      radius: 6,
      fill: new Fill({ color: "#f6e7aa" }),
      stroke: new Stroke({ color: "#22c58f", width: 2 }),
    }),
  }),
});

const markerLayer = new VectorLayer({
  source: markerSource,
  style: (feature) => {
    const label = feature.get("label");
    const type = feature.get("type");
    return new Style({
      image: new CircleStyle({
        radius: type === "center" ? 11 : 8,
        fill: new Fill({ color: type === "center" ? "#0f7e69" : "#0d6657" }),
        stroke: new Stroke({ color: "#f0d58a", width: 2 }),
      }),
      text: new Text({
        text: label,
        offsetY: type === "center" ? -26 : -22,
        fill: new Fill({ color: "#ffffff" }),
        stroke: new Stroke({ color: "rgba(4, 50, 45, 0.92)", width: 5 }),
        font: "bold 13px Microsoft YaHei",
      }),
    });
  },
});

const baseLayers = {
  vector: new TileLayer({ source: new OSM(), visible: true }),
  imagery: new TileLayer({
    source: new XYZ({
      url: import.meta.env.VITE_IMAGERY_TILE_URL || "https://services.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
      attributions: "Imagery tiles are configurable in .env",
    }),
    visible: false,
  }),
  terrain: new TileLayer({
    source: new XYZ({
      url: "https://tiles.wmflabs.org/hillshading/{z}/{x}/{y}.png",
      attributions: "Mock hillshade layer",
    }),
    visible: false,
  }),
};

onMounted(() => {
  map = new Map({
    target: mapEl.value,
    layers: [baseLayers.vector, baseLayers.imagery, baseLayers.terrain, fenceLayer, markerLayer],
    view: new View({
      center: fromLonLat([114.94, 25.836]),
      zoom: 13,
    }),
  });
  map.on("pointermove", (event) => {
    pointerLonLat.value = toLonLat(event.coordinate);
  });
  setDrawInteraction(props.drawType);
});

onBeforeUnmount(() => {
  if (map) map.setTarget(undefined);
});

watch(() => props.baseLayer, updateBaseLayer);
watch(() => props.drawType, setDrawInteraction);
watch(() => props.analysisResult, (result) => {
  markerSource.clear();
  if (result && !result.error && currentFenceFeature) {
    addAnalysisMarkers();
  }
});

function updateBaseLayer(layerName) {
  Object.entries(baseLayers).forEach(([name, layer]) => layer.setVisible(name === layerName));
}

function setDrawInteraction(type) {
  if (!map) return;
  if (drawInteraction) map.removeInteraction(drawInteraction);
  const options = type === "Rectangle"
    ? { source: vectorSource, type: "Circle", geometryFunction: createBox() }
    : { source: vectorSource, type };

  drawInteraction = new Draw(options);
  drawInteraction.on("drawstart", () => clearFence(false));
  drawInteraction.on("drawend", (event) => {
    setTimeout(() => handleFence(event.feature, true), 0);
  });
  map.addInteraction(drawInteraction);
}

function handleFence(feature, shouldFit = false) {
  let geometry = feature.getGeometry();
  if (geometry instanceof CircleGeom) {
    geometry = Polygon.fromCircle(geometry, 96);
    feature = new Feature(geometry);
    vectorSource.clear();
    vectorSource.addFeature(feature);
  }
  currentFenceFeature = feature;
  markerSource.clear();

  const geojson = new GeoJSON().writeFeatureObject(feature, {
    featureProjection: "EPSG:3857",
    dataProjection: "EPSG:4326",
  });
  const info = buildFenceInfo(geometry);
  fenceInfo.value = info;
  addCenterMarker(info);
  if (shouldFit) fitToFence(feature);
  emit("fence-created", { geojson, info });
}

function buildFenceInfo(geometry) {
  const center = toLonLat(geometry.getInteriorPoint ? geometry.getInteriorPoint().getCoordinates() : geometry.getClosestPoint([0, 0]));
  const coords = geometry.getCoordinates()?.[0] || [];
  pointerLonLat.value = center;
  return {
    area_m2: Math.round(getArea(geometry)),
    center_lon: Number(center[0].toFixed(6)),
    center_lat: Number(center[1].toFixed(6)),
    vertex_count: coords.length,
  };
}

function setFenceGeojson(featureGeojson) {
  if (!map) return;
  const feature = new GeoJSON().readFeature(featureGeojson, {
    dataProjection: "EPSG:4326",
    featureProjection: "EPSG:3857",
  });
  vectorSource.clear();
  vectorSource.addFeature(feature);
  handleFence(feature, true);
}

function addCenterMarker(info) {
  markerSource.addFeature(new Feature({
    geometry: new Point(fromLonLat([info.center_lon, info.center_lat])),
    label: "明堂",
    type: "center",
  }));
}

function addAnalysisMarkers() {
  const info = fenceInfo.value;
  if (!info) return;
  const extent = currentFenceFeature.getGeometry().getExtent();
  const minLonLat = toLonLat([extent[0], extent[1]]);
  const maxLonLat = toLonLat([extent[2], extent[3]]);
  const lon = info.center_lon;
  const lat = info.center_lat;
  const dx = (maxLonLat[0] - minLonLat[0]) * 0.34;
  const dy = (maxLonLat[1] - minLonLat[1]) * 0.34;
  const markers = [
    ["靠山", lon, lat + dy, "pattern"],
    ["水口", lon + dx, lat - dy * 0.35, "pattern"],
    ["左辅", lon - dx, lat, "pattern"],
    ["右弼", lon + dx, lat + dy * 0.08, "pattern"],
  ];
  markers.forEach(([label, markerLon, markerLat, type]) => {
    markerSource.addFeature(new Feature({
      geometry: new Point(fromLonLat([markerLon, markerLat])),
      label,
      type,
    }));
  });
}

function fitToFence(feature) {
  map.getView().fit(feature.getGeometry().getExtent(), {
    padding: [96, 96, 96, 96],
    duration: 650,
    maxZoom: 14,
  });
}

function clearFence(emitEvent = true) {
  vectorSource.clear();
  markerSource.clear();
  currentFenceFeature = null;
  fenceInfo.value = null;
  if (emitEvent) emit("fence-cleared");
}

defineExpose({ clearFence, setFenceGeojson });
</script>
