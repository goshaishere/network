<template>
  <q-page padding>
    <div class="text-h5 q-mb-md">{{ $t("home.welcome") }}</div>
    <p class="text-body1 text-grey-8">
      {{ $t("home.blurb") }}
    </p>

    <div v-if="auth.isAuthenticated && auth.user" class="q-mt-md q-gutter-sm row items-center flex-wrap">
      <q-btn color="primary" outline :to="{ name: 'dashboard' }" :label="$t('home.openDashboard')" />
      <q-btn
        color="primary"
        flat
        :to="{ name: 'user-profile', params: { id: String(auth.user.id) } }"
        :label="$t('home.myProfile')"
      />
      <q-btn color="secondary" flat :to="{ name: 'settings-profile' }" :label="$t('home.settings')" />
      <q-btn outline color="primary" :to="{ name: 'communities' }" :label="$t('nav.communities')" />
      <q-btn outline color="primary" :to="{ name: 'messages' }" :label="$t('nav.messages')" />
    </div>
    <div v-else class="q-mt-md q-gutter-sm">
      <q-btn color="primary" :to="{ name: 'auth-login' }" :label="$t('nav.signIn')" />
      <q-btn outline color="primary" :to="{ name: 'auth-register' }" :label="$t('nav.signUp')" />
    </div>

    <div v-if="auth.isAuthenticated && auth.user" class="row q-col-gutter-md q-mt-md">
      <div class="col-12 col-md-6">
        <q-card flat bordered>
          <q-card-section class="row items-center no-wrap">
            <div class="text-subtitle2">{{ $t("home.feedWall") }}</div>
            <q-space />
            <q-btn
              flat
              dense
              color="primary"
              :to="{ name: 'user-profile', params: { id: String(auth.user.id) } }"
              :label="$t('home.all')"
            />
          </q-card-section>
          <q-separator />
          <q-card-section>
            <q-linear-progress v-if="feedLoading" indeterminate color="primary" class="q-mb-sm" />
            <q-banner v-if="feedErr" dense rounded class="bg-warning text-dark">{{ feedErr }}</q-banner>
            <q-list v-else-if="wallSnip.length" dense separator>
              <q-item v-for="p in wallSnip" :key="p.id">
                <q-item-section>
                  <q-item-label caption>{{ p.author_display_name }}</q-item-label>
                  <q-item-label lines="2">{{ p.body }}</q-item-label>
                </q-item-section>
              </q-item>
            </q-list>
            <div v-else class="text-caption text-grey-7">{{ $t("home.feedEmpty") }}</div>
          </q-card-section>
        </q-card>
      </div>
      <div class="col-12 col-md-6">
        <q-card flat bordered>
          <q-card-section class="row items-center no-wrap">
            <div class="text-subtitle2">{{ $t("home.feedMessages") }}</div>
            <q-space />
            <q-btn flat dense color="primary" :to="{ name: 'messages' }" :label="$t('home.all')" />
          </q-card-section>
          <q-separator />
          <q-card-section>
            <q-linear-progress v-if="feedLoading" indeterminate color="primary" class="q-mb-sm" />
            <q-list v-if="convSnip.length" dense separator>
              <q-item
                v-for="c in convSnip"
                :key="c.id"
                v-ripple
                clickable
                :to="{ name: 'conversation', params: { id: String(c.id) } }"
              >
                <q-item-section>
                  <q-item-label>{{ formatConvPeer(c) }}</q-item-label>
                  <q-item-label caption>#{{ c.id }}</q-item-label>
                </q-item-section>
              </q-item>
            </q-list>
            <div v-else-if="!feedLoading" class="text-caption text-grey-7">{{ $t("home.feedEmpty") }}</div>
          </q-card-section>
        </q-card>
      </div>
    </div>

    <q-card flat bordered class="q-mt-md">
      <q-card-section>
        <div class="text-subtitle2 q-mb-sm">{{ $t("home.apiCheck") }}</div>
        <q-btn color="primary" :label="$t('home.healthBtn')" :loading="loading" @click="checkHealth" />
        <pre v-if="healthText" class="q-mt-sm text-caption">{{ healthText }}</pre>
      </q-card-section>
    </q-card>
  </q-page>
</template>

<script setup lang="ts">
import { ref, watch } from "vue";
import axios from "axios";
import { useI18n } from "vue-i18n";
import { api } from "@/api/client";
import { useAuthStore } from "@/stores/auth";
import type { ConversationRow } from "@/types/messaging";
import type { Paginated, WallPost } from "@/types/profile";

const auth = useAuthStore();
const { t } = useI18n();

const loading = ref(false);
const healthText = ref("");

const feedLoading = ref(false);
const feedErr = ref("");
const wallSnip = ref<WallPost[]>([]);
const convSnip = ref<ConversationRow[]>([]);

function formatConvPeer(c: ConversationRow): string {
  if (c.other_display_name) return c.other_display_name;
  if (c.other_user_id != null) return t("messages.peerFallback", { id: c.other_user_id });
  return t("messages.conversationN", { id: c.id });
}

async function loadFeed(userId: number) {
  feedLoading.value = true;
  feedErr.value = "";
  wallSnip.value = [];
  convSnip.value = [];
  try {
    const [wallRes, convRes] = await Promise.all([
      api.get<Paginated<WallPost>>(`/walls/${userId}/posts/`, { params: { page_size: 3 } }),
      api.get<ConversationRow[]>("/messaging/conversations/"),
    ]);
    wallSnip.value = (wallRes.data.results || []).slice(0, 3);
    const conv = Array.isArray(convRes.data) ? convRes.data : [];
    convSnip.value = conv.slice(0, 3);
  } catch {
    feedErr.value = t("home.feedError");
  } finally {
    feedLoading.value = false;
  }
}

watch(
  () => auth.user?.id,
  (id) => {
    if (id) void loadFeed(id);
  },
  { immediate: true }
);

async function checkHealth() {
  loading.value = true;
  healthText.value = "";
  try {
    const base = import.meta.env.VITE_API_URL || "/api/v1";
    const { data } = await axios.get(`${base.replace(/\/$/, "")}/health/`);
    healthText.value = JSON.stringify(data, null, 2);
  } catch (e: unknown) {
    healthText.value = String(e);
  } finally {
    loading.value = false;
  }
}
</script>
