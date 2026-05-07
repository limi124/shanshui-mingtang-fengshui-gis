<template>
  <div class="cesium-overlay">
    <div class="cesium-toolbar">
      <strong>三维地形视图</strong>
      <button @click="flyTop">俯视</button>
      <button @click="flyOblique">倾斜视角</button>
      <button @click="flyPattern">山水格局观察</button>
      <button @click="$emit('close')">关闭</button>
    </div>

    <div class="cesium-warning">{{ statusMessage }}</div>

    <aside class="cesium-legend">
      <h3>三维指标说明</h3>
      <dl>
        <dt>黄色围栏</dt>
        <dd>用户圈定的地块边界，挤出高度用于增强识别，不代表真实建筑高度。</dd>
        <dt>靠山</dt>
        <dd>北侧或后方较高地势。传统视角称为“有背靠”，现代解释为边界、防风和背景地形。</dd>
        <dt>明堂</dt>
        <dd>地块前方或中心开阔空间，代表视野、活动面和场地舒展度。</dd>
        <dt>水口</dt>
        <dd>模拟水系或排水出口方向，正式判断需接入真实河流、沟渠与汇水数据。</dd>
        <dt>左辅 / 右弼</dt>
        <dd>左右两侧围合关系，用于观察藏风和边界感，不代表现实吉凶断语。</dd>
      </dl>
    </aside>

    <div ref="viewerEl" class="cesium-container"></div>
  </div>
</template>

<script setup>
import { onBeforeUnmount, onMounted, ref } from "vue";
import {
  BoundingSphere,
  Cartesian2,
  Cartesian3,
  CesiumTerrainProvider,
  Color,
  HeadingPitchRange,
  Ion,
  Math as CesiumMath,
  NearFarScalar,
  PolygonHierarchy,
  VerticalOrigin,
  buildModuleUrl,
} from "@cesium/engine";
import { Viewer } from "@cesium/widgets";

const props = defineProps({
  fenceGeojson: {
    type: Object,
    default: null,
  },
});

defineEmits(["close"]);

const viewerEl = ref(null);
const statusMessage = ref("正在初始化三维场景...");
let viewer;
let sceneEntities = [];
let center = { lon: 114.94, lat: 25.836 };
let fenceBounds = {
  minLon: 114.925,
  maxLon: 114.972,
  minLat: 25.809,
  maxLat: 25.854,
};

const fallbackFence = {
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
};

onMounted(async () => {
  buildModuleUrl.setBaseUrl("/cesium/");

  const token = import.meta.env.VITE_CESIUM_ION_TOKEN;
  const terrainAssetId = Number(import.meta.env.VITE_CESIUM_TERRAIN_ASSET_ID || 0);
  if (token) Ion.defaultAccessToken = token;

  viewer = new Viewer(viewerEl.value, {
    animation: false,
    timeline: false,
    geocoder: false,
    homeButton: false,
    sceneModePicker: false,
    baseLayerPicker: false,
    navigationHelpButton: false,
    fullscreenButton: false,
    infoBox: false,
    selectionIndicator: false,
    baseLayer: false,
    skyBox: false,
    skyAtmosphere: false,
  });

  viewer.scene.globe.baseColor = Color.fromCssColorString("#2b7768");
  viewer.scene.backgroundColor = Color.fromCssColorString("#071c1a");
  viewer.scene.globe.enableLighting = true;
  viewer.scene.globe.showGroundAtmosphere = false;
  viewer.scene.screenSpaceCameraController.minimumZoomDistance = 800;
  viewer.scene.screenSpaceCameraController.maximumZoomDistance = 30000000;

  await loadIonTerrain(token, terrainAssetId);

  addFence(props.fenceGeojson || fallbackFence);
  addMockTerrainContext();

  setTimeout(() => {
    viewer.resize();
    flyOblique();
  }, 180);
});

onBeforeUnmount(() => {
  viewer?.destroy();
});

async function loadIonTerrain(token, terrainAssetId) {
  if (!token || !terrainAssetId) {
    statusMessage.value = "当前为本地 mock 三维。若要加载 Cesium ion 地形，请配置 token 和 terrain asset id。";
    return;
  }

  try {
    statusMessage.value = `正在加载 Cesium ion 地形资产 ${terrainAssetId}...`;
    const provider = await CesiumTerrainProvider.fromIonAssetId(terrainAssetId, {
      requestVertexNormals: true,
    });
    provider.errorEvent.addEventListener((error) => {
      console.warn("Cesium terrain tile error", error);
      statusMessage.value = `Cesium ion 地形瓦片请求失败：${error.message || "请检查 asset 是否完成切片和 token 权限"}`;
    });
    viewer.terrainProvider = provider;
    statusMessage.value = `已加载 Cesium ion 真实地形资产：${terrainAssetId}`;
  } catch (error) {
    console.error("Cesium terrain load failed", error);
    statusMessage.value = "Cesium ion 地形加载失败，已回退到本地 mock 三维。请检查 token、asset id 和 ion 权限。";
  }
}

function addFence(feature) {
  const coords = feature.geometry.coordinates[0];
  updateBounds(coords);
  // 使用外包框中心作为三维观察中心，避免闭合点或不规则顶点让相机目标偏移。
  center = {
    lon: (fenceBounds.minLon + fenceBounds.maxLon) / 2,
    lat: (fenceBounds.minLat + fenceBounds.maxLat) / 2,
  };

  const positions = Cartesian3.fromDegreesArray(coords.flatMap(([lon, lat]) => [lon, lat]));

  trackEntity(viewer.entities.add({
    name: "用户电子围栏",
    polygon: {
      hierarchy: new PolygonHierarchy(positions),
      material: Color.fromCssColorString("#2bd6a0").withAlpha(0.5),
      outline: true,
      outlineColor: Color.fromCssColorString("#f0d58a"),
      height: 80,
      extrudedHeight: 900,
    },
  }));

  trackEntity(viewer.entities.add({
    name: "围栏边界",
    polyline: {
      positions,
      width: 5,
      material: Color.fromCssColorString("#f0d58a"),
      clampToGround: false,
    },
  }));

  addMarker("明堂", center.lon, center.lat, 1400, Color.fromCssColorString("#f0d58a"));
  addMarker("靠山", center.lon, fenceBounds.maxLat + boundsHeight() * 0.18, 2200, Color.fromCssColorString("#3bd08f"));
  addMarker("水口", fenceBounds.maxLon + boundsWidth() * 0.15, center.lat - boundsHeight() * 0.25, 1500, Color.fromCssColorString("#65d9ff"));
  addMarker("左辅", fenceBounds.minLon - boundsWidth() * 0.1, center.lat, 1600, Color.fromCssColorString("#9be1b6"));
  addMarker("右弼", fenceBounds.maxLon + boundsWidth() * 0.1, center.lat, 1600, Color.fromCssColorString("#9be1b6"));
}

function updateBounds(coords) {
  const lons = coords.map((item) => item[0]);
  const lats = coords.map((item) => item[1]);
  fenceBounds = {
    minLon: Math.min(...lons),
    maxLon: Math.max(...lons),
    minLat: Math.min(...lats),
    maxLat: Math.max(...lats),
  };
}

function boundsWidth() {
  return Math.max(fenceBounds.maxLon - fenceBounds.minLon, 0.01);
}

function boundsHeight() {
  return Math.max(fenceBounds.maxLat - fenceBounds.minLat, 0.01);
}

function cameraHeight(multiplier = 1) {
  const bounds = sceneBounds();
  const widthDegree = bounds.maxLon - bounds.minLon;
  const heightDegree = bounds.maxLat - bounds.minLat;
  const lat = CesiumMath.toRadians(center.lat);
  const widthMeters = widthDegree * 111320 * Math.cos(lat);
  const heightMeters = heightDegree * 110540;
  return Math.max(widthMeters, heightMeters, 4500) * multiplier;
}

function sceneBounds() {
  const xPad = boundsWidth() * 0.42;
  const yPad = boundsHeight() * 0.42;
  return {
    minLon: fenceBounds.minLon - xPad,
    maxLon: fenceBounds.maxLon + xPad,
    minLat: fenceBounds.minLat - yPad,
    maxLat: fenceBounds.maxLat + yPad,
  };
}

function sceneCenter() {
  const bounds = sceneBounds();
  return {
    lon: (bounds.minLon + bounds.maxLon) / 2,
    lat: (bounds.minLat + bounds.maxLat) / 2,
  };
}

function addMockTerrainContext() {
  addSceneBase();
  addRaisedPatch("北侧山势", center.lon, fenceBounds.maxLat + boundsHeight() * 0.22, boundsWidth() * 0.72, boundsHeight() * 0.28, 1600, "#1d8a5f");
  addRaisedPatch("前方明堂", center.lon, fenceBounds.minLat - boundsHeight() * 0.22, boundsWidth() * 0.8, boundsHeight() * 0.26, 500, "#67b889");
  addRaisedPatch("水系低带", fenceBounds.maxLon + boundsWidth() * 0.22, center.lat, boundsWidth() * 0.24, boundsHeight() * 0.85, 260, "#238ba0");
}

function addSceneBase() {
  const bounds = sceneBounds();
  const coords = [
    bounds.minLon, bounds.minLat,
    bounds.maxLon, bounds.minLat,
    bounds.maxLon, bounds.maxLat,
    bounds.minLon, bounds.maxLat,
    bounds.minLon, bounds.minLat,
  ];
  trackEntity(viewer.entities.add({
    name: "三维地形观察基底",
    polygon: {
      hierarchy: Cartesian3.fromDegreesArray(coords),
      material: Color.fromCssColorString("#226f61").withAlpha(0.34),
      outline: true,
      outlineColor: Color.fromCssColorString("#76d6bd").withAlpha(0.55),
      height: 0,
    },
  }));
}

function addRaisedPatch(name, lon, lat, width, height, extrudedHeight, color) {
  const halfW = width / 2;
  const halfH = height / 2;
  const coords = [
    lon - halfW, lat - halfH,
    lon + halfW, lat - halfH,
    lon + halfW, lat + halfH,
    lon - halfW, lat + halfH,
    lon - halfW, lat - halfH,
  ];
  trackEntity(viewer.entities.add({
    name,
    polygon: {
      hierarchy: Cartesian3.fromDegreesArray(coords),
      material: Color.fromCssColorString(color).withAlpha(0.42),
      outline: true,
      outlineColor: Color.WHITE.withAlpha(0.45),
      height: 20,
      extrudedHeight,
    },
  }));
}

function addMarker(label, lon, lat, height, color) {
  trackEntity(viewer.entities.add({
    name: label,
    position: Cartesian3.fromDegrees(lon, lat, height),
    point: {
      pixelSize: 14,
      color,
      outlineColor: Color.WHITE,
      outlineWidth: 2,
      scaleByDistance: new NearFarScalar(1000, 1.3, 50000, 0.8),
    },
    label: {
      text: label,
      font: "bold 15px Microsoft YaHei",
      fillColor: Color.WHITE,
      outlineColor: Color.fromCssColorString("#062d29"),
      outlineWidth: 4,
      style: 2,
      verticalOrigin: VerticalOrigin.BOTTOM,
      pixelOffset: new Cartesian2(0, -18),
      scaleByDistance: new NearFarScalar(1000, 1.15, 50000, 0.75),
    },
  }));
}

function flyTop() {
  flyToScene(-90, 0, 1.55);
}

function flyOblique() {
  flyToScene(-52, 0, 1.85);
}

function flyPattern() {
  flyToScene(-38, 35, 2.15);
}

function trackEntity(entity) {
  sceneEntities.push(entity);
  return entity;
}

function sceneBoundingSphere() {
  const bounds = sceneBounds();
  const samplePoints = [
    [bounds.minLon, bounds.minLat, 0],
    [bounds.maxLon, bounds.minLat, 0],
    [bounds.maxLon, bounds.maxLat, 0],
    [bounds.minLon, bounds.maxLat, 0],
    [center.lon, center.lat, 2600],
    [center.lon, fenceBounds.maxLat + boundsHeight() * 0.22, 2600],
    [fenceBounds.maxLon + boundsWidth() * 0.22, center.lat, 1800],
    [fenceBounds.minLon - boundsWidth() * 0.1, center.lat, 1800],
  ].map(([lon, lat, height]) => Cartesian3.fromDegrees(lon, lat, height));
  return BoundingSphere.fromPoints(samplePoints);
}

function flyToScene(pitchDegree, headingDegree, rangeScale) {
  if (!viewer) return;
  const sphere = sceneBoundingSphere();
  const range = Math.max(sphere.radius * rangeScale, cameraHeight(0.72));
  viewer.camera.flyToBoundingSphere(sphere, {
    offset: new HeadingPitchRange(
      CesiumMath.toRadians(headingDegree),
      CesiumMath.toRadians(pitchDegree),
      range,
    ),
    duration: 1.1,
  });
}
</script>
