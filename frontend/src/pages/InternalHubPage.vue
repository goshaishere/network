<template>
  <q-page padding>
    <div class="text-h6 q-mb-md">{{ $t("internal.title") }}</div>
    <q-banner v-if="errorMsg" rounded dense class="bg-negative text-white q-mb-md">{{ errorMsg }}</q-banner>
    <q-linear-progress v-if="loading" indeterminate color="primary" class="q-mb-md" />
    <q-card v-else flat bordered>
      <q-card-section>
        <pre class="text-body2">{{ JSON.stringify(status, null, 2) }}</pre>
      </q-card-section>
    </q-card>
  </q-page>
</template>

<script setup lang="ts">
import { onMounted, ref } from "vue";
import { useI18n } from "vue-i18n";
import { api } from "@/api/client";

const { t } = useI18n();
const loading = ref(true);
const errorMsg = ref("");
const status = ref<Record<string, unknown> | null>(null);

onMounted(async () => {
  loading.value = true;
  errorMsg.value = "";
  try {
    const { data } = await api.get<Record<string, unknown>>("/internal/status/");
    status.value = data;
  } catch {
    errorMsg.value = t("internal.forbiddenOrError");
  } finally {
    loading.value = false;
  }
});
</script>
