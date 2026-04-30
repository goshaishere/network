<template>
  <q-page padding>
    <div class="text-h6 q-mb-md">{{ $t("friends.title") }}</div>
    <q-banner v-if="errorMsg" rounded dense class="bg-negative text-white q-mb-md">{{ errorMsg }}</q-banner>
    <q-linear-progress v-if="loading" indeterminate color="primary" class="q-mb-md" />

    <div v-else class="q-gutter-y-md">
      <q-card flat bordered>
        <q-card-section class="text-subtitle2">{{ $t("friends.addById") }}</q-card-section>
        <q-card-section class="row q-col-gutter-sm items-end">
          <q-input
            v-model.number="inviteUserId"
            type="number"
            dense
            outlined
            class="col-12 col-sm-4"
            :label="$t('friends.userId')"
          />
          <q-btn color="primary" unelevated :loading="sending" @click="sendRequest">
            {{ $t("friends.sendRequest") }}
          </q-btn>
        </q-card-section>
      </q-card>

      <q-card flat bordered>
        <q-card-section class="text-subtitle2">{{ $t("friends.incoming") }}</q-card-section>
        <q-list v-if="incoming.length" bordered separator>
          <q-item v-for="r in incoming" :key="r.id">
            <q-item-section>
              <q-item-label>{{ r.from_user_detail?.display_name || r.from_user_detail?.email }}</q-item-label>
              <q-item-label caption>id {{ r.from_user }}</q-item-label>
            </q-item-section>
            <q-item-section side>
              <q-btn dense flat color="positive" @click="accept(r.id)">{{ $t("friends.accept") }}</q-btn>
              <q-btn dense flat color="negative" @click="reject(r.id)">{{ $t("friends.reject") }}</q-btn>
            </q-item-section>
          </q-item>
        </q-list>
        <q-card-section v-else class="text-grey">{{ $t("friends.noIncoming") }}</q-card-section>
      </q-card>

      <q-card flat bordered>
        <q-card-section class="text-subtitle2">{{ $t("friends.list") }}</q-card-section>
        <q-list v-if="friends.length" bordered separator>
          <q-item v-for="f in friends" :key="f.id">
            <q-item-section>
              <q-item-label>{{ f.display_name || f.email }}</q-item-label>
              <q-item-label caption>{{ f.email }}</q-item-label>
            </q-item-section>
          </q-item>
        </q-list>
        <q-card-section v-else class="text-grey">{{ $t("friends.empty") }}</q-card-section>
      </q-card>
    </div>
  </q-page>
</template>

<script setup lang="ts">
import { onMounted, ref } from "vue";
import { useI18n } from "vue-i18n";
import { useQuasar } from "quasar";
import { api } from "@/api/client";

interface FriendRow {
  id: number;
  email: string;
  display_name: string;
}

interface IncomingRow {
  id: number;
  from_user: number;
  from_user_detail?: FriendRow;
}

const { t } = useI18n();
const $q = useQuasar();

const loading = ref(true);
const errorMsg = ref("");
const friends = ref<FriendRow[]>([]);
const incoming = ref<IncomingRow[]>([]);
const inviteUserId = ref<number | null>(null);
const sending = ref(false);

async function loadAll() {
  errorMsg.value = "";
  try {
    const [f, inc] = await Promise.all([
      api.get<FriendRow[]>("/social/friends/"),
      api.get<IncomingRow[]>("/social/friend-requests/incoming/"),
    ]);
    friends.value = f.data;
    incoming.value = inc.data;
  } catch {
    errorMsg.value = t("friends.loadError");
  }
}

async function sendRequest() {
  if (!inviteUserId.value) return;
  sending.value = true;
  try {
    await api.post("/social/friend-requests/", { to_user_id: inviteUserId.value });
    $q.notify({ type: "positive", message: t("friends.requestSent") });
    inviteUserId.value = null;
  } catch {
    $q.notify({ type: "negative", message: t("friends.requestFailed") });
  } finally {
    sending.value = false;
  }
}

async function accept(id: number) {
  await api.post(`/social/friend-requests/${id}/accept/`);
  await loadAll();
}

async function reject(id: number) {
  await api.post(`/social/friend-requests/${id}/reject/`);
  await loadAll();
}

onMounted(async () => {
  loading.value = true;
  await loadAll();
  loading.value = false;
});
</script>
