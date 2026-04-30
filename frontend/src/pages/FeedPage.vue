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
  </q-page>
</template>

<script setup lang="ts">
import { ref } from "vue";
import { useI18n } from "vue-i18n";
import { api } from "@/api/client";
import type { FeedItem, FeedResponse } from "@/types/feed";

const { t, locale } = useI18n();

const items = ref<FeedItem[]>([]);
const initialLoading = ref(true);
const loadError = ref("");
let offset = 0;
let exhausted = false;

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
