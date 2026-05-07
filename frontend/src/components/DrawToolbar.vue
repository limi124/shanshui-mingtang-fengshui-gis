<template>
  <section class="panel-section">
    <h2>绘制工具</h2>
    <div class="draw-grid">
      <button :class="{ selected: drawType === 'Polygon' }" @click="$emit('set-draw-type', 'Polygon')">多边形</button>
      <button :class="{ selected: drawType === 'Rectangle' }" @click="$emit('set-draw-type', 'Rectangle')">矩形</button>
      <button :class="{ selected: drawType === 'Circle' }" @click="$emit('set-draw-type', 'Circle')">圆形</button>
      <button :disabled="!hasFence" @click="$emit('clear')">清除围栏</button>
    </div>
  </section>
</template>

<script setup>
defineProps({
  drawType: {
    type: String,
    required: true,
  },
  hasFence: {
    type: Boolean,
    default: false,
  },
});

defineEmits(["set-draw-type", "clear"]);
</script>
