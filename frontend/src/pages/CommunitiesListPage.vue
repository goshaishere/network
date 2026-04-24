<template>
  <q-page padding>
    <div class="row items-center justify-between q-mb-md">
      <div class="text-h6">{{ $t("communities.title") }}</div>
      <q-btn
        v-if="auth.isAuthenticated"
        color="primary"
        icon="add"
        :label="$t('communities.create')"
        @click="openCreate = true"
      />
    </div>

    <q-dialog v-model="openCreate">
      <q-card style="min-width: 320px; max-width: 480px">
        <q-card-section class="text-subtitle1">{{ $t("communities.create") }}</q-card-section>
        <q-card-section class="q-gutter-md">
          <q-input v-model="form.name" outlined :label="$t('communities.name')" />
          <q-input v-model="form.slug" outlined :label="$t('communities.slug')" :hint="$t('communities.slugHint')" />
          <q-input v-model="form.description" outlined type="textarea" :label="$t('communities.description')" />
          <q-toggle v-model="form.is_open" :label="$t('communities.openCommunity')" />
        </q-card-section>
        <q-card-actions align="right">
          <q-btn flat :label="$t('dashboard.cancel')" @click="openCreate = false" />
          <q-btn color="primary" :loading="creating" :label="$t('communities.submit')" @click="submitCreate" />
        </q-card-actions>
      </q-card>
    </q-dialog>

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
          <q-badge v-if="!c.is_open" color="grey-8">{{ $t("communities.closed") }}</q-badge>
          <q-badge v-else outline color="primary">{{ $t("communities.open") }}</q-badge>
          <div class="text-caption q-mt-xs">{{ c.members_count }} {{ $t("communities.members") }}</div>
        </q-item-section>
      </q-item>
    </q-list>
    <div v-else-if="!loading && !loadError" class="text-body2 text-grey-7">{{ $t("communities.empty") }}</div>

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
import { onMounted, reactive, ref } from "vue";
import { useQuasar } from "quasar";
import { useI18n } from "vue-i18n";
import { api } from "@/api/client";
import { toRelativeApiPath } from "@/lib/apiUrl";
import { useAuthStore } from "@/stores/auth";
import type { CommunityListItem, PaginatedCommunities } from "@/types/community";

const auth = useAuthStore();
const $q = useQuasar();
const { t } = useI18n();

const loading = ref(true);
const loadingMore = ref(false);
const loadError = ref("");
const items = ref<CommunityListItem[]>([]);
const nextUrl = ref<string | null>(null);

const openCreate = ref(false);
const creating = ref(false);
const form = reactive({ name: "", slug: "", description: "", is_open: true });

async function fetchFirst() {
  loading.value = true;
  loadError.value = "";
  try {
    const { data } = await api.get<PaginatedCommunities>("/communities/");
    items.value = data.results;
    nextUrl.value = data.next;
  } catch (e: unknown) {
    loadError.value = String(e);
  } finally {
    loading.value = false;
  }
}

async function loadMore() {
  if (!nextUrl.value) return;
  loadingMore.value = true;
  try {
    const { data } = await api.get<PaginatedCommunities>(toRelativeApiPath(nextUrl.value));
    items.value.push(...data.results);
    nextUrl.value = data.next;
  } finally {
    loadingMore.value = false;
  }
}

async function submitCreate() {
  const slug = form.slug.trim().toLowerCase().replace(/\s+/g, "-");
  if (!form.name.trim() || !slug) {
    $q.notify({ type: "warning", message: t("communities.fillRequired") });
    return;
  }
  creating.value = true;
  try {
    await api.post("/communities/", {
      name: form.name.trim(),
      slug,
      description: form.description.trim(),
      is_open: form.is_open,
    });
    openCreate.value = false;
    form.name = "";
    form.slug = "";
    form.description = "";
    form.is_open = true;
    await fetchFirst();
  } catch (e: unknown) {
    $q.notify({ type: "negative", message: String(e) });
  } finally {
    creating.value = false;
  }
}

onMounted(fetchFirst);
</script>
