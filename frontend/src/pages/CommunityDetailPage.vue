<template>
  <q-page padding>
    <q-linear-progress v-if="loading" indeterminate color="primary" class="q-mb-md" />
    <q-banner v-if="errorMsg" rounded dense class="bg-negative text-white q-mb-md">{{ errorMsg }}</q-banner>

    <template v-if="community && !errorMsg">
      <div class="text-h6">{{ community.name }}</div>
      <div class="text-caption text-grey-7 q-mb-md">
        /{{ community.slug }} · {{ community.members_count }} {{ $t("communities.members") }}
      </div>
      <p class="text-body2" style="white-space: pre-wrap">{{ community.description || "—" }}</p>

      <div v-if="auth.isAuthenticated" class="q-mt-md q-gutter-sm">
        <q-btn
          v-if="!community.is_member"
          color="primary"
          outline
          :label="community.is_open ? $t('communities.join') : $t('communities.joinClosed')"
          :loading="joining"
          :disable="!community.is_open"
          @click="doJoin"
        />
        <q-badge v-else color="positive" outline>{{ $t("communities.youAreMember") }}</q-badge>
      </div>

      <q-separator class="q-my-lg" />

      <div class="text-subtitle1 q-mb-sm">{{ $t("communities.postsTitle") }}</div>
      <q-banner v-if="postsError" dense rounded class="bg-warning text-dark q-mb-sm">{{ postsError }}</q-banner>

      <q-card v-if="auth.isAuthenticated && community.is_member" flat bordered class="q-mb-md">
        <q-card-section>
          <q-input v-model="newBody" outlined type="textarea" autogrow :rows="2" :label="$t('communities.newPost')" />
          <q-btn
            class="q-mt-sm"
            color="primary"
            :label="$t('communities.publish')"
            :loading="posting"
            :disable="!newBody.trim()"
            @click="submitPost"
          />
        </q-card-section>
      </q-card>

      <q-list v-if="posts.length" bordered separator class="rounded-borders">
        <q-item v-for="p in posts" :key="p.id" class="q-py-md">
          <q-item-section>
            <q-item-label caption>#{{ p.author_id }} · {{ formatDate(p.created_at) }}</q-item-label>
            <q-item-label class="q-mt-xs" style="white-space: pre-wrap">{{ p.body }}</q-item-label>
          </q-item-section>
        </q-item>
      </q-list>
      <div v-else-if="!postsLoading" class="text-body2 text-grey-7">{{ $t("communities.noPosts") }}</div>
      <q-inner-loading :showing="postsLoading" />

      <q-btn
        v-if="postsNext"
        flat
        color="primary"
        class="q-mt-md"
        :loading="loadingMorePosts"
        :label="$t('profile.loadMore')"
        @click="loadMorePosts"
      />
    </template>
  </q-page>
</template>

<script setup lang="ts">
import { computed, ref, watch } from "vue";
import { useRoute } from "vue-router";
import { useQuasar } from "quasar";
import { useI18n } from "vue-i18n";
import { api } from "@/api/client";
import { toRelativeApiPath } from "@/lib/apiUrl";
import { useAuthStore } from "@/stores/auth";
import type { CommunityDetail, CommunityPost, PaginatedPosts } from "@/types/community";

const route = useRoute();
const auth = useAuthStore();
const $q = useQuasar();
const { t, locale } = useI18n();

const slug = computed(() => String(route.params.slug || ""));

const loading = ref(true);
const errorMsg = ref("");
const community = ref<CommunityDetail | null>(null);

const postsLoading = ref(false);
const postsError = ref("");
const posts = ref<CommunityPost[]>([]);
const postsNext = ref<string | null>(null);
const loadingMorePosts = ref(false);
const posting = ref(false);
const joining = ref(false);
const newBody = ref("");

function formatDate(iso: string): string {
  try {
    return new Intl.DateTimeFormat(locale.value === "en" ? "en" : "ru", {
      dateStyle: "short",
      timeStyle: "short",
    }).format(new Date(iso));
  } catch {
    return iso;
  }
}

async function loadCommunity() {
  loading.value = true;
  errorMsg.value = "";
  community.value = null;
  try {
    const { data } = await api.get<CommunityDetail>(`/communities/${slug.value}/`);
    community.value = data;
  } catch {
    errorMsg.value = t("communities.notFound");
  } finally {
    loading.value = false;
  }
}

async function loadPosts() {
  postsLoading.value = true;
  postsError.value = "";
  posts.value = [];
  postsNext.value = null;
  try {
    const { data } = await api.get<PaginatedPosts>(`/communities/${slug.value}/posts/`);
    posts.value = data.results;
    postsNext.value = data.next;
  } catch (e: unknown) {
    if (community.value?.is_member || community.value?.is_open) {
      postsError.value = String(e);
    } else {
      postsError.value = t("communities.postsPrivate");
    }
  } finally {
    postsLoading.value = false;
  }
}

async function loadMorePosts() {
  if (!postsNext.value) return;
  loadingMorePosts.value = true;
  try {
    const { data } = await api.get<PaginatedPosts>(toRelativeApiPath(postsNext.value));
    posts.value.push(...data.results);
    postsNext.value = data.next;
  } finally {
    loadingMorePosts.value = false;
  }
}

async function doJoin() {
  joining.value = true;
  try {
    await api.post(`/communities/${slug.value}/join/`, {});
    $q.notify({ type: "positive", message: t("communities.joined") });
    await loadCommunity();
    await loadPosts();
  } catch (e: unknown) {
    $q.notify({ type: "negative", message: String(e) });
  } finally {
    joining.value = false;
  }
}

async function submitPost() {
  if (!newBody.value.trim()) return;
  posting.value = true;
  try {
    const { data } = await api.post<CommunityPost>(`/communities/${slug.value}/posts/`, {
      body: newBody.value.trim(),
    });
    posts.value.unshift(data);
    newBody.value = "";
  } catch (e: unknown) {
    $q.notify({ type: "negative", message: String(e) });
  } finally {
    posting.value = false;
  }
}

watch(
  slug,
  async (s) => {
    if (!s) return;
    await loadCommunity();
    await loadPosts();
  },
  { immediate: true }
);
</script>
