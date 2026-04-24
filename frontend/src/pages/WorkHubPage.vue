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
            <q-item v-for="b in boards" :key="b.id" clickable :active="selectedBoardId === b.id" @click="selectBoard(b.id)">
              <q-item-section>{{ b.name }}</q-item-section>
              <q-item-section side>{{ b.preset }}</q-item-section>
            </q-item>
          </q-list>
          <div class="row q-col-gutter-sm">
            <div v-for="col in columns" :key="col.id" class="col-12 col-md-4">
              <q-card flat bordered>
                <q-card-section class="text-subtitle2">{{ col.title }}</q-card-section>
                <q-separator />
                <q-list dense>
                  <q-item v-for="task in tasksByColumn(col.id)" :key="task.id">
                    <q-item-section>
                      <q-item-label>{{ task.title }}</q-item-label>
                      <q-item-label caption>{{ task.due_date || "-" }}</q-item-label>
                    </q-item-section>
                  </q-item>
                </q-list>
              </q-card>
            </div>
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
import { onMounted, ref } from "vue";
import { useQuasar } from "quasar";
import { useI18n } from "vue-i18n";
import { api } from "@/api/client";
import type { WorkBoard, WorkColumn, WorkGroup, WorkTask } from "@/types/work";

const { t } = useI18n();
const $q = useQuasar();

const loading = ref(true);
const errorMsg = ref("");
const groups = ref<WorkGroup[]>([]);
const boards = ref<WorkBoard[]>([]);
const columns = ref<WorkColumn[]>([]);
const tasks = ref<WorkTask[]>([]);
const selectedGroupId = ref<number | null>(null);
const selectedBoardId = ref<number | null>(null);

function tasksByColumn(columnId: number) {
  return tasks.value.filter((x) => x.column === columnId);
}

async function loadGroups() {
  const { data } = await api.get<WorkGroup[]>("/tasks/groups/");
  groups.value = data;
  selectedGroupId.value = data[0]?.id ?? null;
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
    await loadBoards();
    await loadBoardData();
  } catch {
    errorMsg.value = t("work.loadError");
  } finally {
    loading.value = false;
  }
}

async function selectGroup(groupId: number) {
  selectedGroupId.value = groupId;
  await loadBoards();
  await loadBoardData();
}

async function selectBoard(boardId: number) {
  selectedBoardId.value = boardId;
  await loadBoardData();
}

async function createGroup() {
  const name = window.prompt(t("work.promptGroupName"));
  if (!name) return;
  const slug = name.toLowerCase().replaceAll(/\s+/g, "-").replaceAll(/[^a-z0-9-]/g, "");
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

onMounted(async () => {
  await refreshAll();
});
</script>
