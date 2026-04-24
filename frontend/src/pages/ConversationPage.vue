<template>
  <q-page padding class="column" style="height: calc(100vh - 50px)">
    <div class="row items-center no-wrap q-mb-sm">
      <q-btn flat round dense icon="arrow_back" :to="{ name: 'messages' }" />
      <div class="text-subtitle1 ellipsis q-ml-xs">{{ $t("messages.chatTitle") }} #{{ convId }}</div>
      <q-space />
      <q-badge :color="connected ? 'positive' : 'grey'" text-color="white" outline>
        {{ connected ? $t("messages.wsOn") : $t("messages.wsOff") }}
      </q-badge>
    </div>

    <q-banner v-if="lastError" dense rounded class="bg-warning text-dark q-mb-xs">{{ lastError }}</q-banner>
    <q-banner v-if="loadError" dense rounded class="bg-negative text-white q-mb-xs">{{ loadError }}</q-banner>
    <q-linear-progress v-if="loading" indeterminate color="primary" class="q-mb-xs" />

    <q-scroll-area class="col" style="min-height: 0">
      <div class="q-pa-sm">
        <q-btn
          v-if="olderNext"
          flat
          dense
          size="sm"
          color="primary"
          class="q-mb-sm"
          :loading="loadingOlder"
          :label="$t('messages.loadOlder')"
          @click="loadOlder"
        />
        <div v-for="m in messages" :key="m.id" class="q-mb-xs">
          <q-chat-message
            :name="isMine(m) ? $t('messages.you') : $t('messages.peer', { id: m.sender_id })"
            :text="[m.body]"
            :sent="isMine(m)"
            :stamp="formatTime(m.created_at)"
          />
        </div>
        <div ref="bottomEl" style="height: 1px" />
      </div>
    </q-scroll-area>

    <q-separator />
    <div class="q-pa-sm row items-end q-gutter-sm no-wrap">
      <q-input
        v-model="draft"
        class="col"
        outlined
        type="textarea"
        autogrow
        :rows="1"
        :label="$t('messages.write')"
      />
      <q-btn color="primary" icon="send" :loading="sending" :disable="!draft.trim()" @click="send" />
    </div>
  </q-page>
</template>

<script setup lang="ts">
import { computed, nextTick, ref, watch } from "vue";
import { storeToRefs } from "pinia";
import { useRoute } from "vue-router";
import { useQuasar } from "quasar";
import { useI18n } from "vue-i18n";
import { api } from "@/api/client";
import { useMessagingSocket } from "@/composables/useMessagingSocket";
import { toRelativeApiPath } from "@/lib/apiUrl";
import { useAuthStore } from "@/stores/auth";
import type { ChatMessage, CursorPage } from "@/types/messaging";

const route = useRoute();
const $q = useQuasar();
const auth = useAuthStore();
const { tokenGeneration } = storeToRefs(auth);
const { t, locale } = useI18n();

const convId = computed(() => Number(route.params.id));

const messages = ref<ChatMessage[]>([]);
const loading = ref(false);
const loadError = ref("");
const olderNext = ref<string | null>(null);
const loadingOlder = ref(false);
const sending = ref(false);
const draft = ref("");
const bottomEl = ref<InstanceType<typeof globalThis.Element> | null>(null);

const { connected, lastError, connect, disconnect, subscribe } = useMessagingSocket();

function isMine(m: ChatMessage): boolean {
  return auth.user?.id === m.sender_id;
}

function formatTime(iso: string): string {
  try {
    const d = new Date(iso);
    return new Intl.DateTimeFormat(locale.value === "en" ? "en" : "ru", {
      dateStyle: "short",
      timeStyle: "short",
    }).format(d);
  } catch {
    return iso;
  }
}

function scrollBottom() {
  bottomEl.value?.scrollIntoView({ block: "end" });
}

function appendIncoming(m: ChatMessage) {
  if (messages.value.some((x) => x.id === m.id)) return;
  messages.value = [...messages.value, m];
  void nextTick(() => scrollBottom());
}

async function loadMessages(id: number) {
  loading.value = true;
  loadError.value = "";
  try {
    const { data } = await api.get<CursorPage<ChatMessage>>(`/messaging/conversations/${id}/messages/`);
    messages.value = [...data.results].sort((a, b) => a.id - b.id);
    olderNext.value = data.next;
    await nextTick();
    scrollBottom();
  } catch {
    loadError.value = t("messages.loadFailed");
  } finally {
    loading.value = false;
  }
}

async function loadOlder() {
  if (!olderNext.value) return;
  loadingOlder.value = true;
  try {
    const { data } = await api.get<CursorPage<ChatMessage>>(toRelativeApiPath(olderNext.value));
    const older = [...data.results].sort((a, b) => a.id - b.id);
    const merged = [...older, ...messages.value];
    const seen = new Set<number>();
    messages.value = merged
      .filter((m) => {
        if (seen.has(m.id)) return false;
        seen.add(m.id);
        return true;
      })
      .sort((a, b) => a.id - b.id);
    olderNext.value = data.next;
  } catch {
    $q.notify({ type: "negative", message: t("messages.loadOlderFailed") });
  } finally {
    loadingOlder.value = false;
  }
}

async function send() {
  const text = draft.value.trim();
  if (!text) return;
  sending.value = true;
  try {
    const { data } = await api.post<ChatMessage>(`/messaging/conversations/${convId.value}/messages/`, {
      body: text,
    });
    if (!messages.value.some((x) => x.id === data.id)) {
      messages.value = [...messages.value, data];
    }
    draft.value = "";
    await nextTick();
    scrollBottom();
  } catch {
    $q.notify({ type: "negative", message: t("messages.sendFailed") });
  } finally {
    sending.value = false;
  }
}

watch(
  convId,
  (id) => {
    if (!Number.isFinite(id) || id < 1) return;
    disconnect();
    messages.value = [];
    olderNext.value = null;
    connect(appendIncoming);
    void loadMessages(id);
  },
  { immediate: true }
);

watch(connected, (ok) => {
  if (ok && Number.isFinite(convId.value) && convId.value > 0) {
    subscribe(convId.value);
  }
});

watch(tokenGeneration, () => {
  if (!Number.isFinite(convId.value) || convId.value < 1) return;
  if (!auth.accessToken) return;
  disconnect();
  connect(appendIncoming);
});
</script>
