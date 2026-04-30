<template>
  <q-page padding>
    <div class="row items-center justify-between q-mb-md">
      <div class="text-h6">{{ $t("communities.mineTitle") }}</div>
      <q-btn flat color="primary" :to="{ name: 'communities' }" :label="$t('communities.browseAll')" />
    </div>
    <q-banner v-if="loadError" rounded dense class="bg-negative text-white q-mb-md">{{ loadError }}</q-banner>
    <q-linear-progress v-if="loading" indeterminate color="primary" class="q-mb-md" />
    <q-list v-if="items.length" bordered separator class="rounded-borders">
      <q-item
        v-for="c in items"
        :key="c.id"
        v-ripple
        clickable
        :to="{ name: 'community-detail', params: { slug: c.slug } }"
      >
        <q-item-section>
          <q-item-label>{{ c.name }}</q-item-label>
          <q-item-label caption lines="2">{{ c.description || "—" }}</q-item-label>
        </q-item-section>
        <q-item-section side>
          <div class="text-caption">{{ c.members_count }} {{ $t("communities.members") }}</div>
        </q-item-section>
      </q-item>
    </q-list>
    <div v-else-if="!loading && !loadError" class="text-body2 text-grey-7">{{ $t("communities.mineEmpty") }}</div>
    <q-btn
      v-if="nextUrl"
      flat
      color="primary"
      class="q-mt-md"
      :loading="loadingMore"
      :label="$t('profile.loadMore')"
      @click="loadMore"
    />
  </q-page>
</template>

<script setup lang="ts">
import { onMounted, ref } from "vue";
import { useI18n } from "vue-i18n";
import { api } from "@/api/client";
import { toRelativeApiPath } from "@/lib/apiUrl";
import type { CommunityListItem, PaginatedCommunities } from "@/types/community";

const { t } = useI18n();
const loading = ref(true);
const loadingMore = ref(false);
const loadError = ref("");
const items = ref<CommunityListItem[]>([]);
const nextUrl = ref<string | null>(null);

async function fetchFirst() {
  loading.value = true;
  loadError.value = "";
  try {
    const { data } = await api.get<PaginatedCommunities>("/communities/mine/");
    items.value = data.results;
    nextUrl.value = data.next;
  } catch {
    loadError.value = t("communities.loadError");
  } finally {
    loading.value = false;
  }
}

async function loadMore() {
  if (!nextUrl.value) return;
  loadingMore.value = true;
  try {
    const path = toRelativeApiPath(nextUrl.value);
    const { data } = await api.get<PaginatedCommunities>(path);
    items.value.push(...data.results);
    nextUrl.value = data.next;
  } finally {
    loadingMore.value = false;
  }
}

onMounted(() => void fetchFirst());
</script>
