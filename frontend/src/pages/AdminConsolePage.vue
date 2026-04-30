<template>
  <q-page padding>
    <div class="text-h6 q-mb-md">{{ $t("console.stubTitle") }}</div>
    <q-tabs v-model="tab" dense class="q-mb-md" align="left">
      <q-tab name="users" :label="$t('console.tabUsers')" />
      <q-tab name="groups" :label="$t('console.tabGroups')" />
    </q-tabs>

    <q-tab-panels v-model="tab" animated>
      <q-tab-panel name="users" class="q-pa-none">
        <q-banner v-if="errorMsg" rounded dense class="bg-negative text-white q-mb-md">{{ errorMsg }}</q-banner>
        <q-linear-progress v-if="loadingUsers" indeterminate color="primary" class="q-mb-md" />
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
      </q-tab-panel>

      <q-tab-panel name="groups" class="q-pa-none">
        <q-banner v-if="groupsError" rounded dense class="bg-negative text-white q-mb-md">{{ groupsError }}</q-banner>
        <q-linear-progress v-if="loadingGroups" indeterminate color="primary" class="q-mb-md" />
        <div v-else class="q-gutter-y-md">
          <div class="text-subtitle2">{{ $t("console.groupsTitle") }}</div>
          <q-list bordered separator class="q-mb-md">
            <q-item v-for="g in groups" :key="g.id">
              <q-item-section>
                <q-item-label>{{ g.name }} ({{ g.slug }})</q-item-label>
                <q-item-label caption>{{ (g.permission_slugs || []).join(", ") }}</q-item-label>
              </q-item-section>
            </q-item>
          </q-list>
          <div class="row q-col-gutter-sm items-end">
            <q-input v-model="newGroupName" dense outlined class="col-12 col-sm-3" :label="$t('console.groupName')" />
            <q-input v-model="newGroupSlug" dense outlined class="col-12 col-sm-3" :label="$t('console.groupSlug')" />
            <q-select
              v-model="newGroupPerms"
              multiple
              dense
              outlined
              use-chips
              emit-value
              map-options
              class="col-12 col-sm-4"
              :options="catalogOptions"
              :label="$t('console.permissions')"
            />
            <q-btn color="primary" unelevated :loading="creatingGroup" @click="createGroup">
              {{ $t("console.createGroup") }}
            </q-btn>
          </div>
        </div>
      </q-tab-panel>
    </q-tab-panels>
  </q-page>
</template>

<script setup lang="ts">
import { onMounted, ref, watch } from "vue";
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

interface PermissionGroupRow {
  id: number;
  name: string;
  slug: string;
  description: string;
  permission_slugs: string[];
  member_ids: number[];
}

const { t } = useI18n();
const tab = ref<"users" | "groups">("users");
const loadingUsers = ref(true);
const loadingGroups = ref(false);
const errorMsg = ref("");
const groupsError = ref("");
const rows = ref<AdminUserRow[]>([]);
const groups = ref<PermissionGroupRow[]>([]);
const catalogOptions = ref<{ label: string; value: string }[]>([]);
const newGroupName = ref("");
const newGroupSlug = ref("");
const newGroupPerms = ref<string[]>([]);
const creatingGroup = ref(false);

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

async function loadGroupsPanel() {
  loadingGroups.value = true;
  groupsError.value = "";
  try {
    const [cat, grp] = await Promise.all([
      api.get<{ slug: string; name: string }[]>("/admin/permission-catalog/"),
      api.get<PermissionGroupRow[]>("/admin/permission-groups/"),
    ]);
    catalogOptions.value = cat.data.map((x) => ({ label: `${x.slug} — ${x.name}`, value: x.slug }));
    groups.value = grp.data;
  } catch {
    groupsError.value = t("console.loadGroupsError");
  } finally {
    loadingGroups.value = false;
  }
}

async function saveRow(row: AdminUserRow) {
  try {
    await api.patch("/admin/users/", row);
  } catch {
    errorMsg.value = t("common.stubBody");
  }
}

async function createGroup() {
  if (!newGroupName.value.trim() || !newGroupSlug.value.trim()) return;
  creatingGroup.value = true;
  try {
    await api.post("/admin/permission-groups/", {
      name: newGroupName.value.trim(),
      slug: newGroupSlug.value.trim().toLowerCase().replaceAll(/\s+/g, "-"),
      description: "",
      permission_slugs: newGroupPerms.value,
      member_ids: [],
    });
    newGroupName.value = "";
    newGroupSlug.value = "";
    newGroupPerms.value = [];
    await loadGroupsPanel();
  } catch {
    groupsError.value = t("console.loadGroupsError");
  } finally {
    creatingGroup.value = false;
  }
}

watch(tab, (v) => {
  if (v === "groups") void loadGroupsPanel();
});

onMounted(async () => {
  loadingUsers.value = true;
  errorMsg.value = "";
  try {
    await loadUsers();
  } catch {
    errorMsg.value = t("common.stubBody");
  } finally {
    loadingUsers.value = false;
  }
});
</script>
