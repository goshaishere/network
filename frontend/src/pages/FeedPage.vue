<template>
  <q-page padding>
    <div class="text-h6 q-mb-md">{{ $t("feed.title") }}</div>
    <p class="text-body2 text-grey-7 q-mb-md">{{ $t("feed.subtitle") }}</p>

    <q-banner v-if="loadError" rounded dense class="bg-negative text-white q-mb-md">{{ loadError }}</q-banner>

    <q-list v-if="items.length" bordered separator class="rounded-borders">
      <q-item v-for="(it, idx) in items" :key="`${it.type}-${it.id}-${idx}`" align="top" class="q-py-md">
        <q-item-section avatar>
          <q-icon :name="it.type === 'wall' ? 'article' : 'groups'" color="primary" />
        </q-item-section>
        <q-item-section>
          <q-item-label caption>
            <template v-if="it.type === 'wall'">
              <router-link :to="{ name: 'user-profile', params: { id: String(it.wall_owner_id) } }" class="text-primary">
                {{ it.wall_owner_display_name || $t("feed.wallOf", { id: it.wall_owner_id }) }}
              </router-link>
              · {{ it.author_display_name || $t("profile.authorFallback", { id: it.author_id }) }}
            </template>
            <template v-else>
              <router-link :to="{ name: 'community-detail', params: { slug: it.community_slug } }" class="text-primary">
                {{ it.community_name }}
              </router-link>
              · {{ it.author_display_name || $t("profile.authorFallback", { id: it.author_id }) }}
            </template>
          </q-item-label>
          <q-item-label caption>{{ formatDate(it.created_at) }}</q-item-label>
          <q-item-label class="q-mt-xs" style="white-space: pre-wrap">{{ it.body }}</q-item-label>
          <div v-if="it.attachment_url" class="q-mt-sm">
            <q-img
              :src="it.attachment_url"
              :alt="$t('feed.attachmentAlt')"
              fit="contain"
              style="max-height: 280px; max-width: 100%"
              class="rounded-borders"
            />
          </div>
        </q-item-section>
        <q-item-section v-if="auth.isAuthenticated" side top>
          <q-btn flat dense round icon="flag" color="grey-7" @click="openReport(it)">
            <q-tooltip>{{ $t("feed.report") }}</q-tooltip>
          </q-btn>
        </q-item-section>
      </q-item>
    </q-list>
    <div v-else-if="!initialLoading && !loadError" class="text-body2 text-grey-7">{{ $t("feed.empty") }}</div>

    <q-inner-loading :showing="initialLoading && !items.length" />

    <q-infinite-scroll :offset="200" :disable="!!loadError" @load="onInfiniteLoad">
      <template #loading>
        <div class="row justify-center q-my-md">
          <q-spinner color="primary" size="2em" />
        </div>
      </template>
    </q-infinite-scroll>

    <q-dialog v-model="reportOpen">
      <q-card style="min-width: 320px; max-width: 480px">
        <q-card-section class="text-subtitle1">{{ $t("feed.reportTitle") }}</q-card-section>
        <q-card-section class="q-pt-none text-body2 text-grey-8">{{ $t("feed.reportHint") }}</q-card-section>
        <q-card-section>
          <q-input v-model="reportReason" type="textarea" autogrow outlined :label="$t('feed.reportReason')" />
        </q-card-section>
        <q-card-actions align="right">
          <q-btn v-close-popup flat :label="$t('profile.cancel')" />
          <q-btn color="primary" :loading="reportSending" :label="$t('feed.reportSend')" @click="submitReport" />
        </q-card-actions>
      </q-card>
    </q-dialog>
  </q-page>
</template>

<script setup lang="ts">
import { ref } from "vue";
import { useQuasar } from "quasar";
import { useI18n } from "vue-i18n";
import { api } from "@/api/client";
import { useAuthStore } from "@/stores/auth";
import type { FeedItem, FeedResponse } from "@/types/feed";

const { t, locale } = useI18n();
const $q = useQuasar();
const auth = useAuthStore();

const items = ref<FeedItem[]>([]);
const initialLoading = ref(true);
const loadError = ref("");
let offset = 0;
let exhausted = false;

const reportOpen = ref(false);
const reportTarget = ref<FeedItem | null>(null);
const reportReason = ref("");
const reportSending = ref(false);

function formatDate(iso: string): string {
  try {
    const d = new Date(iso);
    return new Intl.DateTimeFormat(locale.value === "en" ? "en" : "ru", {
      dateStyle: "medium",
      timeStyle: "short",
    }).format(d);
  } catch {
    return iso;
  }
}

function openReport(it: FeedItem) {
  reportTarget.value = it;
  reportReason.value = "";
  reportOpen.value = true;
}

async function submitReport() {
  const it = reportTarget.value;
  if (!it) return;
  reportSending.value = true;
  try {
    await api.post("/social/reports/", {
      target_type: it.type === "wall" ? "wall_post" : "community_post",
      target_id: it.id,
      reason: reportReason.value.trim(),
    });
    reportOpen.value = false;
    $q.notify({ type: "positive", message: t("feed.reportSent") });
  } catch {
    $q.notify({ type: "negative", message: t("feed.reportFailed") });
  } finally {
    reportSending.value = false;
  }
}

async function fetchChunk(): Promise<void> {
  const { data } = await api.get<FeedResponse>("/social/feed/", { params: { offset } });
  items.value.push(...data.results);
  if (data.next_offset == null) {
    exhausted = true;
  } else {
    offset = data.next_offset;
  }
}

async function onInfiniteLoad(_index: number, done: (stop?: boolean) => void) {
  if (exhausted) {
    initialLoading.value = false;
    done(true);
    return;
  }
  try {
    await fetchChunk();
    initialLoading.value = false;
    done(exhausted);
  } catch {
    loadError.value = t("feed.loadError");
    initialLoading.value = false;
    done(true);
  }
}
</script>
