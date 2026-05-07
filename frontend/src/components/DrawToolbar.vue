<template>
  <section class="panel-section">
    <h2>{{ labels.title }}</h2>
    <div class="draw-grid">
      <button :class="{ selected: drawType === 'Polygon' }" @click="$emit('set-draw-type', 'Polygon')">{{ labels.polygon }}</button>
      <button :class="{ selected: drawType === 'Rectangle' }" @click="$emit('set-draw-type', 'Rectangle')">{{ labels.rectangle }}</button>
      <button :class="{ selected: drawType === 'Circle' }" @click="$emit('set-draw-type', 'Circle')">{{ labels.circle }}</button>
      <button :disabled="!hasFence" @click="$emit('clear')">{{ labels.clear }}</button>
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
  labels: {
    type: Object,
    required: true,
  },
});

defineEmits(["set-draw-type", "clear"]);
</script>
