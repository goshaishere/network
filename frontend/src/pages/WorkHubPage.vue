<template>
  <q-page padding>
    <div class="row items-center q-col-gutter-sm q-mb-md">
      <div class="col">
        <div class="text-h6">{{ $t("work.title") }}</div>
      </div>
      <div class="col-auto">
        <q-btn color="primary" dense unelevated @click="createGroup">{{ $t("work.newGroup") }}</q-btn>
      </div>
    </div>
    <q-banner v-if="errorMsg" rounded dense class="bg-negative text-white q-mb-md">{{ errorMsg }}</q-banner>
    <q-banner v-if="showPartnerNotice" rounded dense class="bg-info text-white q-mb-md">
      {{ $t("work.partnerInternalNotice") }}
    </q-banner>
    <q-card v-if="showInternalSummary" flat bordered class="q-mb-md">
      <q-card-section class="text-subtitle2">{{ $t("work.internalSummaryTitle") }}</q-card-section>
      <q-separator />
      <q-card-section v-if="internalError" class="text-negative">{{ internalError }}</q-card-section>
      <q-card-section v-else-if="internalSummary">
        <div class="text-body2">
          {{ $t("work.internalOpenTasks") }}:
          <strong>{{ internalSummary.internal?.open_tasks_estimate ?? "—" }}</strong>
        </div>
        <div v-if="internalSummary.internal?.crm_readiness" class="text-caption text-grey q-mt-sm">
          {{ internalSummary.internal.crm_readiness.note }}
        </div>
      </q-card-section>
      <q-linear-progress v-else indeterminate color="primary" class="q-ma-md" />
    </q-card>
    <q-linear-progress v-if="loading" indeterminate color="primary" class="q-mb-md" />
    <template v-else>
      <div class="row q-col-gutter-md">
        <div class="col-12 col-md-4">
          <q-list bordered separator>
            <q-item-label header>{{ $t("work.groups") }}</q-item-label>
            <q-item
              v-for="g in groups"
              :key="g.id"
              clickable
              :active="selectedGroupId === g.id"
              @click="selectGroup(g.id)"
            >
              <q-item-section>
                <q-item-label>{{ g.name }}</q-item-label>
                <q-item-label caption>{{ g.members_count }} {{ $t("work.members") }}</q-item-label>
              </q-item-section>
            </q-item>
          </q-list>
        </div>
        <div class="col-12 col-md-8">
          <div class="row items-center q-col-gutter-sm q-mb-sm">
            <div class="col">
              <div class="text-subtitle1">{{ $t("work.boards") }}</div>
            </div>
            <div class="col-auto">
              <q-btn dense flat color="primary" @click="createBoard">{{ $t("work.newBoard") }}</q-btn>
            </div>
          </div>
          <q-list bordered separator class="q-mb-md">
            <q-item
              v-for="b in boards"
              :key="b.id"
              clickable
              :active="selectedBoardId === b.id"
              @click="selectBoard(b.id)"
            >
              <q-item-section>{{ b.name }}</q-item-section>
              <q-item-section side>{{ b.preset }}</q-item-section>
            </q-item>
          </q-list>

          <div v-if="selectedBoardId && columnsSorted.length" class="kanban-scroll">
            <draggable
              v-model="columnsSorted"
              item-key="id"
              class="row no-wrap q-col-gutter-sm"
              handle=".column-drag-handle"
              @end="onColumnsDragEnd"
            >
              <template #item="{ element: col }">
                <div class="kanban-column">
                  <q-card flat bordered class="full-height">
                    <q-card-section class="row items-center q-pb-sm">
                      <q-icon
                        name="drag_indicator"
                        class="column-drag-handle cursor-move q-mr-sm"
                        size="sm"
                      />
                      <span class="text-subtitle2">{{ col.title }}</span>
                    </q-card-section>
                    <q-separator />
                    <q-card-section class="q-pt-sm">
                      <draggable
                        :model-value="taskLists[col.id] || []"
                        item-key="id"
                        group="board-tasks"
                        class="column-tasks"
                        @update:model-value="(v) => setTaskList(col.id, v)"
                        @end="onTasksDragEnd"
                      >
                        <template #item="{ element: task }">
                          <q-item dense class="rounded-borders q-mb-xs bg-grey-9">
                            <q-item-section>
                              <q-item-label>{{ task.title }}</q-item-label>
                              <q-item-label caption>{{ task.due_date || "—" }}</q-item-label>
                            </q-item-section>
                          </q-item>
                        </template>
                      </draggable>
                    </q-card-section>
                  </q-card>
                </div>
              </template>
            </draggable>
          </div>
          <q-btn v-if="selectedBoardId" class="q-mt-md" dense outline color="primary" @click="createTask">
            {{ $t("work.newTask") }}
          </q-btn>
        </div>
      </div>
    </template>
  </q-page>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, watch } from "vue";
import { useRoute, useRouter } from "vue-router";
import draggable from "vuedraggable";
import { useQuasar } from "quasar";
import { useI18n } from "vue-i18n";
import { api } from "@/api/client";
import { useAuthStore } from "@/stores/auth";
import type { WorkBoard, WorkColumn, WorkGroup, WorkTask } from "@/types/work";

const { t } = useI18n();
const $q = useQuasar();
const auth = useAuthStore();
const route = useRoute();
const router = useRouter();

const showInternalSummary = computed(
  () => Boolean(auth.user?.is_employee && auth.user?.employment_kind === "internal")
);
const showPartnerNotice = computed(
  () => Boolean(auth.user?.is_employee && auth.user?.employment_kind === "partner")
);

const internalSummary = ref<{
  internal?: { open_tasks_estimate?: number; crm_readiness?: { note?: string } };
} | null>(null);
const internalError = ref("");

const loading = ref(true);
const errorMsg = ref("");
const groups = ref<WorkGroup[]>([]);
const boards = ref<WorkBoard[]>([]);
const columns = ref<WorkColumn[]>([]);
const columnsSorted = ref<WorkColumn[]>([]);
const tasks = ref<WorkTask[]>([]);
const taskLists = ref<Record<number, WorkTask[]>>({});
const selectedGroupId = ref<number | null>(null);
const selectedBoardId = ref<number | null>(null);

function rebuildTaskLists() {
  const m: Record<number, WorkTask[]> = {};
  for (const col of columns.value) {
    m[col.id] = [...tasks.value.filter((x) => x.column === col.id)].sort(
      (a, b) => a.position - b.position || a.id - b.id
    );
  }
  taskLists.value = m;
}

function setTaskList(columnId: number, list: WorkTask[]) {
  taskLists.value = { ...taskLists.value, [columnId]: list };
}

watch(
  () => columns.value,
  () => {
    columnsSorted.value = [...columns.value].sort((a, b) => a.position - b.position || a.id - b.id);
    rebuildTaskLists();
  },
  { deep: true }
);

watch(
  () => tasks.value,
  () => rebuildTaskLists(),
  { deep: true }
);

async function loadGroups() {
  const { data } = await api.get<WorkGroup[]>("/tasks/groups/");
  groups.value = data;
}

function applyRouteGroupId() {
  const raw = route.params.groupId;
  if (raw === undefined || raw === "") {
    selectedGroupId.value = groups.value[0]?.id ?? null;
    return;
  }
  const gid = Number(Array.isArray(raw) ? raw[0] : raw);
  if (Number.isFinite(gid) && groups.value.some((g) => g.id === gid)) {
    selectedGroupId.value = gid;
    return;
  }
  selectedGroupId.value = groups.value[0]?.id ?? null;
}

async function loadBoards() {
  if (!selectedGroupId.value) {
    boards.value = [];
    return;
  }
  const { data } = await api.get<WorkBoard[]>("/tasks/boards/", { params: { group: selectedGroupId.value } });
  boards.value = data;
  selectedBoardId.value = data[0]?.id ?? null;
}

async function loadBoardData() {
  if (!selectedBoardId.value) {
    columns.value = [];
    tasks.value = [];
    return;
  }
  const [columnsResp, tasksResp] = await Promise.all([
    api.get<WorkColumn[]>("/tasks/columns/", { params: { board: selectedBoardId.value } }),
    api.get<WorkTask[]>("/tasks/", { params: { board: selectedBoardId.value } }),
  ]);
  columns.value = columnsResp.data;
  tasks.value = tasksResp.data;
}

async function refreshAll() {
  loading.value = true;
  errorMsg.value = "";
  try {
    await loadGroups();
    applyRouteGroupId();
    await loadBoards();
    await loadBoardData();
  } catch {
    errorMsg.value = t("work.loadError");
  } finally {
    loading.value = false;
  }
}

async function selectGroup(groupId: number) {
  await router.push({
    name: "work-group-detail",
    params: { groupId: String(groupId) },
  });
}

async function selectBoard(boardId: number) {
  selectedBoardId.value = boardId;
  await loadBoardData();
}

async function createGroup() {
  const name = window.prompt(t("work.promptGroupName"));
  if (!name) return;
  const slug = name
    .toLowerCase()
    .replaceAll(/\s+/g, "-")
    .replaceAll(/[^a-z0-9-]/g, "");
  await api.post("/tasks/groups/", { name, slug, description: "" });
  await refreshAll();
}

async function createBoard() {
  if (!selectedGroupId.value) return;
  const name = window.prompt(t("work.promptBoardName"));
  if (!name) return;
  await api.post("/tasks/boards/", { group: selectedGroupId.value, name, preset: "generic_pm" });
  await loadBoards();
  await loadBoardData();
}

async function createTask() {
  if (!selectedBoardId.value || columns.value.length === 0) return;
  const title = window.prompt(t("work.promptTaskTitle"));
  if (!title) return;
  await api.post("/tasks/", {
    board: selectedBoardId.value,
    column: columns.value[0].id,
    title,
    description: "",
    due_date: null,
    assignee: null,
  });
  await loadBoardData();
  $q.notify({ type: "positive", message: t("work.taskCreated") });
}

async function onColumnsDragEnd() {
  if (!selectedBoardId.value || columnsSorted.value.length === 0) return;
  const order = columnsSorted.value.map((c) => c.id);
  try {
    await api.post("/tasks/columns/reorder/", { board: selectedBoardId.value, order });
    await loadBoardData();
  } catch {
    errorMsg.value = t("work.loadError");
  }
}

async function onTasksDragEnd() {
  if (!selectedBoardId.value) return;
  try {
    const byId = new Map(tasks.value.map((x) => [x.id, x]));
    const updates: Promise<unknown>[] = [];
    for (const col of columnsSorted.value) {
      const list = taskLists.value[col.id] || [];
      let pos = 0;
      for (const tsk of list) {
        const prev = byId.get(tsk.id);
        if (!prev) continue;
        if (prev.column !== col.id || prev.position !== pos) {
          updates.push(api.patch(`/tasks/${tsk.id}/`, { column: col.id, position: pos }));
        }
        pos += 1;
      }
    }
    await Promise.all(updates);
    await loadBoardData();
  } catch {
    errorMsg.value = t("work.loadError");
    await loadBoardData();
  }
}

async function loadInternalSummary() {
  internalError.value = "";
  internalSummary.value = null;
  if (!showInternalSummary.value) return;
  try {
    const { data } = await api.get("/internal/work/dashboard/");
    internalSummary.value = data;
  } catch {
    internalError.value = t("work.internalLoadError");
  }
}

watch(showInternalSummary, (v) => {
  if (v) void loadInternalSummary();
});

watch(
  () => route.params.groupId,
  async () => {
    if (!route.path.startsWith("/work")) return;
    loading.value = true;
    errorMsg.value = "";
    try {
      await loadGroups();
      applyRouteGroupId();
      await loadBoards();
      await loadBoardData();
    } catch {
      errorMsg.value = t("work.loadError");
    } finally {
      loading.value = false;
    }
  }
);

onMounted(async () => {
  await refreshAll();
  await loadInternalSummary();
});
</script>

<style scoped>
.kanban-scroll {
  overflow-x: auto;
  padding-bottom: 8px;
}
.kanban-column {
  flex: 0 0 280px;
  max-width: 320px;
}
.column-tasks {
  min-height: 40px;
}
</style>
