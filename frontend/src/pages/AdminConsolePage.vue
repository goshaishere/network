<template>
  <q-page padding>
    <div class="text-h6 q-mb-md">{{ $t("console.stubTitle") }}</div>
    <q-banner v-if="errorMsg" rounded dense class="bg-negative text-white q-mb-md">{{ errorMsg }}</q-banner>
    <q-linear-progress v-if="loading" indeterminate color="primary" class="q-mb-md" />
    <q-table v-else :rows="rows" :columns="columns" row-key="id" flat bordered>
      <template #body-cell-is_employee="props">
        <q-td :props="props">
          <q-toggle v-model="props.row.is_employee" @update:model-value="saveRow(props.row)" />
        </q-td>
      </template>
      <template #body-cell-is_staff="props">
        <q-td :props="props">
          <q-toggle v-model="props.row.is_staff" @update:model-value="saveRow(props.row)" />
        </q-td>
      </template>
      <template #body-cell-employment_kind="props">
        <q-td :props="props">
          <q-select
            v-model="props.row.employment_kind"
            dense
            outlined
            emit-value
            map-options
            :options="employmentKinds"
            @update:model-value="saveRow(props.row)"
          />
        </q-td>
      </template>
    </q-table>
  </q-page>
</template>

<script setup lang="ts">
import { onMounted, ref } from "vue";
import { useI18n } from "vue-i18n";
import { api } from "@/api/client";

interface AdminUserRow {
  id: number;
  email: string;
  display_name: string;
  is_staff: boolean;
  is_employee: boolean;
  employment_kind: "" | "internal" | "partner";
}

const { t } = useI18n();
const loading = ref(true);
const errorMsg = ref("");
const rows = ref<AdminUserRow[]>([]);
const employmentKinds = [
  { label: "-", value: "" },
  { label: "internal", value: "internal" },
  { label: "partner", value: "partner" },
];
const columns = [
  { name: "id", label: "ID", field: "id", align: "left" as const },
  { name: "email", label: "Email", field: "email", align: "left" as const },
  { name: "display_name", label: "Имя", field: "display_name", align: "left" as const },
  { name: "is_staff", label: "Admin", field: "is_staff", align: "left" as const },
  { name: "is_employee", label: "Employee", field: "is_employee", align: "left" as const },
  { name: "employment_kind", label: "Kind", field: "employment_kind", align: "left" as const },
];

async function loadUsers() {
  const { data } = await api.get<AdminUserRow[]>("/admin/users/");
  rows.value = data;
}

async function saveRow(row: AdminUserRow) {
  try {
    await api.patch("/admin/users/", row);
  } catch {
    errorMsg.value = t("common.stubBody");
  }
}

onMounted(async () => {
  loading.value = true;
  try {
    await loadUsers();
  } catch {
    errorMsg.value = t("common.stubBody");
  } finally {
    loading.value = false;
  }
});
</script>
