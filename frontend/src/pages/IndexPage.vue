<template>
  <q-page padding>
    <div class="text-h5 q-mb-md">{{ $t("home.welcome") }}</div>
    <p class="text-body1 text-grey-8">
      {{ $t("home.blurb") }}
    </p>
    <q-card flat bordered class="q-mt-md">
      <q-card-section>
        <div class="text-subtitle2 q-mb-sm">{{ $t("home.apiCheck") }}</div>
        <q-btn color="primary" :label="$t('home.healthBtn')" :loading="loading" @click="checkHealth" />
        <pre v-if="healthText" class="q-mt-sm text-caption">{{ healthText }}</pre>
      </q-card-section>
    </q-card>
  </q-page>
</template>

<script setup lang="ts">
import { ref } from "vue";
import axios from "axios";

const loading = ref(false);
const healthText = ref("");

async function checkHealth() {
  loading.value = true;
  healthText.value = "";
  try {
    const base = import.meta.env.VITE_API_URL || "/api/v1";
    const { data } = await axios.get(`${base.replace(/\/$/, "")}/health/`);
    healthText.value = JSON.stringify(data, null, 2);
  } catch (e: unknown) {
    healthText.value = String(e);
  } finally {
    loading.value = false;
  }
}
</script>
