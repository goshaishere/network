<template>
  <q-page padding>
    <div class="text-h6 q-mb-md">{{ $t("work.title") }}</div>
    <q-banner v-if="errorMsg" rounded dense class="bg-negative text-white q-mb-md">{{ errorMsg }}</q-banner>
    <q-linear-progress v-if="loading" indeterminate color="primary" class="q-mb-md" />
    <template v-else-if="payload">
      <p class="text-body2 text-grey-8">{{ payload.note }}</p>
      <q-card flat bordered class="q-mt-md">
        <q-card-section class="text-caption">
          <pre style="margin: 0; white-space: pre-wrap">{{ JSON.stringify(payload, null, 2) }}</pre>
        </q-card-section>
      </q-card>
    </template>
  </q-page>
</template>

<script setup lang="ts">
import { onMounted, ref } from "vue";
import { useI18n } from "vue-i18n";
import { api } from "@/api/client";

const { t } = useI18n();

const loading = ref(true);
const errorMsg = ref("");
const payload = ref<{
  tasks_due: unknown[];
  groups: unknown[];
  boards: unknown[];
  note: string;
} | null>(null);

onMounted(async () => {
  loading.value = true;
  errorMsg.value = "";
  try {
    const { data } = await api.get("/work/dashboard/");
    payload.value = data;
  } catch {
    errorMsg.value = t("work.loadError");
  } finally {
    loading.value = false;
  }
});
</script>
