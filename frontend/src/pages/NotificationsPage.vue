<template>
  <q-page padding>
    <div class="row items-center q-mb-md">
      <div class="text-h6 col">Notifications</div>
      <q-btn dense outline color="primary" label="Read all" @click="markAllRead" />
    </div>
    <q-list bordered separator>
      <q-item v-for="n in notifications" :key="n.id">
        <q-item-section>
          <q-item-label>{{ n.title }}</q-item-label>
          <q-item-label caption>{{ n.body || "—" }}</q-item-label>
        </q-item-section>
        <q-item-section side>
          <q-btn v-if="!n.is_read" flat dense color="primary" label="Read" @click="markRead(n.id)" />
        </q-item-section>
      </q-item>
    </q-list>
  </q-page>
</template>

<script setup lang="ts">
import { onMounted, ref } from "vue";
import { api } from "@/api/client";

interface NotificationRow {
  id: number;
  title: string;
  body: string;
  is_read: boolean;
}

const notifications = ref<NotificationRow[]>([]);

async function load() {
  const { data } = await api.get<NotificationRow[]>("/notifications/");
  notifications.value = data;
}

async function markRead(id: number) {
  await api.post(`/notifications/${id}/read/`);
  await load();
}

async function markAllRead() {
  await api.post("/notifications/read-all/");
  await load();
}

onMounted(load);
</script>
