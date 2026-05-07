<template>
  <section class="panel-section">
    <h2>{{ labels.title }}</h2>
    <button class="side-action active" :class="{ selected: modelValue === 'vector' }" @click="$emit('update:modelValue', 'vector')">
      <span class="layer-icon"></span>{{ labels.vector }}
    </button>
    <button class="side-action" :class="{ selected: modelValue === 'imagery' }" @click="$emit('update:modelValue', 'imagery')">
      <span class="image-icon"></span>{{ labels.imagery }}
    </button>
    <button class="side-action" :class="{ selected: modelValue === 'terrain' }" @click="$emit('update:modelValue', 'terrain')">
      <span class="terrain-icon"></span>{{ labels.terrain }}
    </button>
  </section>
</template>

<script setup>
defineProps({
  modelValue: {
    type: String,
    required: true,
  },
  labels: {
    type: Object,
    required: true,
  },
});

defineEmits(["update:modelValue"]);
</script>
