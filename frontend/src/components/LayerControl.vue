<template>
  <section class="panel-section">
    <h2>底图切换</h2>
    <button class="side-action active" :class="{ selected: modelValue === 'vector' }" @click="$emit('update:modelValue', 'vector')">
      <span class="layer-icon"></span>矢量底图
    </button>
    <button class="side-action" :class="{ selected: modelValue === 'imagery' }" @click="$emit('update:modelValue', 'imagery')">
      <span class="image-icon"></span>影像底图
    </button>
    <button class="side-action" :class="{ selected: modelValue === 'terrain' }" @click="$emit('update:modelValue', 'terrain')">
      <span class="terrain-icon"></span>地形阴影
    </button>
  </section>
</template>

<script setup>
defineProps({
  modelValue: {
    type: String,
    required: true,
  },
});

defineEmits(["update:modelValue"]);
</script>
