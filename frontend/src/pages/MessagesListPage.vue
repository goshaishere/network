<template>
  <q-page padding>
    <div class="row items-center justify-between q-mb-md">
      <div class="text-h6">{{ $t("messages.listTitle") }}</div>
      <q-btn color="primary" icon="add_comment" :label="$t('messages.newChat')" @click="openNew = true" />
    </div>

    <q-dialog v-model="openNew">
      <q-card style="min-width: 300px">
        <q-card-section class="text-subtitle1">{{ $t("messages.newChat") }}</q-card-section>
        <q-card-section>
          <q-input
            v-model="newParticipantId"
            outlined
            type="number"
            :label="$t('messages.participantId')"
            :hint="$t('messages.participantHint')"
          />
        </q-card-section>
        <q-card-actions align="right">
          <q-btn flat :label="$t('dashboard.cancel')" @click="openNew = false" />
          <q-btn color="primary" :label="$t('messages.open')" :loading="creating" @click="createConversation" />
        </q-card-actions>
      </q-card>
    </q-dialog>

    <q-banner v-if="loadError" rounded dense class="bg-negative text-white q-mb-md">{{ loadError }}</q-banner>
    <q-linear-progress v-if="loading" indeterminate color="primary" class="q-mb-md" />

    <q-list v-if="!loading && conversations.length" bordered separator class="rounded-borders">
      <q-item
        v-for="c in conversations"
        :key="c.id"
        v-ripple
        clickable
        :to="{ name: 'conversation', params: { id: String(c.id) } }"
      >
        <q-item-section avatar>
          <q-icon name="chat" color="primary" />
        </q-item-section>
        <q-item-section>
          <q-item-label>{{ formatPeer(c) }}</q-item-label>
          <q-item-label caption>#{{ c.id }} · {{ c.kind }}</q-item-label>
        </q-item-section>
        <q-item-section side>
          <q-icon name="chevron_right" />
        </q-item-section>
      </q-item>
    </q-list>
    <div v-else-if="!loading && !loadError" class="text-body2 text-grey-7">{{ $t("messages.emptyList") }}</div>
  </q-page>
</template>

<script setup lang="ts">
import { onMounted, ref } from "vue";
import { useRouter } from "vue-router";
import { useI18n } from "vue-i18n";
import { api } from "@/api/client";
import type { ConversationRow } from "@/types/messaging";

const router = useRouter();
const { t } = useI18n();

const loading = ref(true);
const loadError = ref("");
const conversations = ref<ConversationRow[]>([]);

const openNew = ref(false);
const newParticipantId = ref("");
const creating = ref(false);

function formatPeer(c: ConversationRow): string {
  if (c.other_display_name) return c.other_display_name;
  if (c.other_user_id != null) return t("messages.peerFallback", { id: c.other_user_id });
  return t("messages.conversationN", { id: c.id });
}

async function fetchList() {
  loading.value = true;
  loadError.value = "";
  try {
    const { data } = await api.get<ConversationRow[]>("/messaging/conversations/");
    conversations.value = Array.isArray(data) ? data : [];
  } catch (e: unknown) {
    loadError.value = String(e);
  } finally {
    loading.value = false;
  }
}

async function createConversation() {
  const id = Number(newParticipantId.value);
  if (!Number.isFinite(id) || id < 1) return;
  creating.value = true;
  try {
    const { data } = await api.post<ConversationRow>("/messaging/conversations/", { participant_id: id });
    openNew.value = false;
    newParticipantId.value = "";
    await router.push({ name: "conversation", params: { id: String(data.id) } });
    await fetchList();
  } catch {
    loadError.value = t("messages.createFailed");
  } finally {
    creating.value = false;
  }
}

onMounted(fetchList);
</script>
