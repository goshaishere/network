<template>
  <q-page padding>
    <div class="row items-center justify-between q-mb-md">
      <div class="text-h6">{{ $t("dashboard.title") }}</div>
      <div class="row q-gutter-sm items-center">
        <q-toggle v-model="editMode" color="primary" :label="$t('dashboard.editMode')" />
        <q-btn
          v-if="editMode"
          outline
          color="primary"
          icon="add"
          :label="$t('dashboard.addWidget')"
          @click="openAddDialog"
        />
        <q-btn
          color="primary"
          :label="$t('dashboard.save')"
          :loading="saving"
          :disable="!dirty || saving"
          @click="saveLayout"
        />
      </div>
    </div>

    <q-banner v-if="loadError" rounded dense class="bg-negative text-white q-mb-md">{{ loadError }}</q-banner>
    <q-linear-progress v-if="loading" indeterminate color="primary" class="q-mb-md" />

    <div v-if="!loading && !loadError" class="row q-col-gutter-md">
      <div v-for="w in displayWidgets" :key="w.id" class="col-12 col-sm-6 col-md-4">
        <q-card flat bordered :class="w.pinned ? 'dashboard-card--pinned' : ''">
          <q-card-section class="q-pb-none">
            <div class="row items-start no-wrap">
              <div class="text-subtitle2 ellipsis col">{{ widgetTitle(w) }}</div>
              <q-badge v-if="w.pinned" color="amber" text-color="black" class="q-ml-sm">
                {{ $t("dashboard.pinned") }}
              </q-badge>
            </div>
          </q-card-section>
          <q-card-section>
            <template v-if="w.type === 'note'">
              <div class="text-body2 text-grey-8" style="white-space: pre-wrap">{{ w.body }}</div>
            </template>
            <template v-else>
              <a :href="w.url" target="_blank" rel="noopener noreferrer" class="text-primary">{{ w.url }}</a>
            </template>
          </q-card-section>
          <q-card-actions v-if="editMode" align="right" class="q-pt-none">
            <q-btn flat dense icon="push_pin" :color="w.pinned ? 'amber' : 'grey'" @click="togglePin(w.id)" />
            <q-btn flat dense icon="keyboard_arrow_up" :disable="!canMoveUp(w.id)" @click="moveUp(w.id)" />
            <q-btn flat dense icon="keyboard_arrow_down" :disable="!canMoveDown(w.id)" @click="moveDown(w.id)" />
            <q-btn flat dense icon="edit" @click="openEditDialog(w)" />
            <q-btn flat dense icon="delete" color="negative" @click="removeWidget(w.id)" />
          </q-card-actions>
        </q-card>
      </div>
      <div v-if="displayWidgets.length === 0" class="col-12 text-body2 text-grey-7">
        {{ $t("dashboard.empty") }}
      </div>
    </div>

    <q-dialog v-model="dialogOpen">
      <q-card style="min-width: 320px; max-width: 480px">
        <q-card-section class="text-subtitle1">{{ dialogTitle }}</q-card-section>
        <q-card-section v-if="dialogMode === 'add'" class="q-gutter-sm">
          <q-btn-toggle
            v-model="addType"
            spread
            no-caps
            toggle-color="primary"
            :options="[
              { label: $t('dashboard.typeNote'), value: 'note' },
              { label: $t('dashboard.typeLink'), value: 'link' },
            ]"
          />
        </q-card-section>
        <q-card-section class="q-gutter-md">
          <q-input v-model="formTitle" outlined :label="$t('dashboard.fieldTitle')" />
          <q-input
            v-if="dialogMode === 'add' ? addType === 'note' : editing?.type === 'note'"
            v-model="formBody"
            outlined
            type="textarea"
            autogrow
            :label="$t('dashboard.fieldBody')"
          />
          <q-input
            v-if="dialogMode === 'add' ? addType === 'link' : editing?.type === 'link'"
            v-model="formUrl"
            outlined
            :label="$t('dashboard.fieldUrl')"
          />
        </q-card-section>
        <q-card-actions align="right">
          <q-btn flat :label="$t('dashboard.cancel')" @click="dialogOpen = false" />
          <q-btn color="primary" :label="$t('dashboard.ok')" @click="confirmDialog" />
        </q-card-actions>
      </q-card>
    </q-dialog>
  </q-page>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, watch } from "vue";
import { useI18n } from "vue-i18n";
import { api } from "@/api/client";
import { emptyLayout, newId, normalizeLayout, sortedWidgets } from "@/lib/dashboardLayout";
import type { DashboardLayoutPayload, DashboardWidget } from "@/types/profile";

const { t } = useI18n();

const loading = ref(true);
const saving = ref(false);
const loadError = ref("");
const editMode = ref(false);
const layout = ref<DashboardLayoutPayload>(emptyLayout());
const savedSnapshot = ref("");
const dirty = computed(() => JSON.stringify(layout.value) !== savedSnapshot.value);

const dialogOpen = ref(false);
const dialogMode = ref<"add" | "edit">("add");
const addType = ref<"note" | "link">("note");
const editing = ref<DashboardWidget | null>(null);
const formTitle = ref("");
const formBody = ref("");
const formUrl = ref("");

const displayWidgets = computed(() => {
  if (editMode.value) return [...layout.value.widgets];
  return sortedWidgets(layout.value.widgets);
});

const dialogTitle = computed(() =>
  dialogMode.value === "add" ? t("dashboard.addWidget") : t("dashboard.editWidget")
);

function widgetTitle(w: DashboardWidget): string {
  return w.title || (w.type === "note" ? t("dashboard.typeNote") : t("dashboard.typeLink"));
}

function snapshot() {
  savedSnapshot.value = JSON.stringify(layout.value);
}

function findIndex(id: string): number {
  return layout.value.widgets.findIndex((x) => x.id === id);
}

function canMoveUp(id: string): boolean {
  return findIndex(id) > 0;
}

function canMoveDown(id: string): boolean {
  const i = findIndex(id);
  return i >= 0 && i < layout.value.widgets.length - 1;
}

function swap(i: number, j: number) {
  const w = [...layout.value.widgets];
  [w[i], w[j]] = [w[j], w[i]];
  layout.value = { ...layout.value, widgets: w };
}

function moveUp(id: string) {
  const i = findIndex(id);
  if (i > 0) swap(i, i - 1);
}

function moveDown(id: string) {
  const i = findIndex(id);
  if (i >= 0 && i < layout.value.widgets.length - 1) swap(i, i + 1);
}

function togglePin(id: string) {
  const w = layout.value.widgets.map((x) =>
    x.id === id ? { ...x, pinned: !x.pinned } : x
  ) as DashboardWidget[];
  layout.value = { ...layout.value, widgets: w };
}

function removeWidget(id: string) {
  layout.value = {
    ...layout.value,
    widgets: layout.value.widgets.filter((x) => x.id !== id),
  };
}

function openAddDialog() {
  dialogMode.value = "add";
  editing.value = null;
  addType.value = "note";
  formTitle.value = "";
  formBody.value = "";
  formUrl.value = "https://";
  dialogOpen.value = true;
}

function openEditDialog(w: DashboardWidget) {
  dialogMode.value = "edit";
  editing.value = w;
  formTitle.value = w.title;
  formBody.value = w.type === "note" ? w.body : "";
  formUrl.value = w.type === "link" ? w.url : "";
  dialogOpen.value = true;
}

function confirmDialog() {
  if (dialogMode.value === "add") {
    const id = newId();
    if (addType.value === "note") {
      layout.value.widgets.push({
        id,
        type: "note",
        title: formTitle.value.trim() || t("dashboard.typeNote"),
        body: formBody.value,
        pinned: false,
      });
    } else {
      layout.value.widgets.push({
        id,
        type: "link",
        title: formTitle.value.trim() || t("dashboard.typeLink"),
        url: formUrl.value.trim() || "https://",
        pinned: false,
      });
    }
  } else if (editing.value) {
    const id = editing.value.id;
    const idx = findIndex(id);
    if (idx < 0) return;
    const cur = layout.value.widgets[idx];
    if (cur.type === "note") {
      layout.value.widgets[idx] = {
        ...cur,
        title: formTitle.value.trim() || t("dashboard.typeNote"),
        body: formBody.value,
      };
    } else {
      layout.value.widgets[idx] = {
        ...cur,
        title: formTitle.value.trim() || t("dashboard.typeLink"),
        url: formUrl.value.trim() || cur.url,
      };
    }
  }
  dialogOpen.value = false;
}

async function fetchLayout() {
  loading.value = true;
  loadError.value = "";
  try {
    const { data } = await api.get<{ layout: unknown }>("/profiles/me/dashboard/");
    layout.value = normalizeLayout(data.layout);
    snapshot();
  } catch (e: unknown) {
    loadError.value = String(e);
  } finally {
    loading.value = false;
  }
}

async function saveLayout() {
  saving.value = true;
  try {
    const { data } = await api.patch<{ layout: unknown }>("/profiles/me/dashboard/", {
      layout: layout.value,
    });
    layout.value = normalizeLayout(data.layout);
    snapshot();
  } finally {
    saving.value = false;
  }
}

onMounted(fetchLayout);

watch(editMode, (on) => {
  if (!on) {
    dialogOpen.value = false;
  }
});
</script>

<style scoped>
.dashboard-card--pinned {
  border-color: var(--q-amber);
  box-shadow: 0 0 0 1px rgba(255, 193, 7, 0.35);
}
</style>
