<template>
  <q-page padding>
    <div class="text-h6">{{ $t(titleKey) }}</div>
    <p class="text-body2 text-grey-7 q-mt-sm">{{ $t(bodyKey) }}</p>
  </q-page>
</template>

<script setup lang="ts">
import { computed } from "vue";
import { useRoute } from "vue-router";

const route = useRoute();
const titleKey = computed(() => String(route.meta.titleKey || "common.unknown"));
const bodyKey = computed(() => String(route.meta.stubBodyKey || "common.stubBody"));
</script>
