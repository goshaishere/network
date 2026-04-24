<template>
  <q-page padding>
    <q-linear-progress v-if="loadingProfile" indeterminate color="primary" class="q-mb-md" />
    <q-banner v-if="profileError" rounded dense class="bg-negative text-white q-mb-md">{{ profileError }}</q-banner>

    <template v-if="profile && !profileError">
      <div class="row q-col-gutter-lg">
        <div class="col-12 col-md-4">
          <q-card flat bordered>
            <q-card-section>
              <div class="text-h6">{{ profile.display_name || $t("profile.unnamed") }}</div>
              <div v-if="profile.bio" class="text-body2 text-grey-8 q-mt-sm" style="white-space: pre-wrap">
                {{ profile.bio }}
              </div>
              <div v-else class="text-caption text-grey-6">{{ $t("profile.noBio") }}</div>
              <q-btn
                v-if="auth.isAuthenticated && auth.user && auth.user.id !== userId"
                class="q-mt-md"
                color="secondary"
                outline
                icon="mail"
                :label="$t('profile.writeMessage')"
                :loading="startingChat"
                @click="startDirect"
              />
            </q-card-section>
          </q-card>
        </div>
        <div class="col-12 col-md-8">
          <div class="text-subtitle1 q-mb-sm">{{ $t("profile.wallTitle") }}</div>
          <q-card v-if="auth.isAuthenticated" flat bordered class="q-mb-md">
            <q-card-section>
              <q-input
                v-model="newPostBody"
                outlined
                type="textarea"
                autogrow
                :rows="2"
                :label="$t('profile.wallNewPost')"
              />
              <q-btn
                class="q-mt-sm"
                color="primary"
                :label="$t('profile.wallPublish')"
                :loading="posting"
                :disable="!newPostBody.trim()"
                @click="submitPost"
              />
            </q-card-section>
          </q-card>

          <q-banner v-if="wallError" rounded dense class="bg-warning text-dark q-mb-sm">{{ wallError }}</q-banner>

          <q-list v-if="posts.length" bordered separator class="rounded-borders">
            <q-item v-for="p in posts" :key="p.id" align="top" class="q-py-md">
              <q-item-section>
                <q-item-label class="text-weight-medium">
                  {{ p.author_display_name || $t("profile.authorFallback", { id: p.author_id }) }}
                </q-item-label>
                <q-item-label caption>{{ formatDate(p.created_at) }}</q-item-label>
                <q-item-label class="q-mt-xs" style="white-space: pre-wrap">{{ p.body }}</q-item-label>
                <div v-if="canEditPost(p)" class="q-mt-sm">
                  <template v-if="editingId === p.id">
                    <q-input v-model="editBody" outlined type="textarea" autogrow dense />
                    <q-btn flat dense color="primary" class="q-mt-xs" @click="saveEdit(p.id)">
                      {{ $t("profile.save") }}
                    </q-btn>
                    <q-btn flat dense class="q-mt-xs" @click="cancelEdit">
                      {{ $t("profile.cancel") }}
                    </q-btn>
                  </template>
                  <template v-else>
                    <q-btn flat dense size="sm" icon="edit" @click="startEdit(p)" />
                    <q-btn flat dense size="sm" icon="delete" color="negative" @click="confirmDelete(p)" />
                  </template>
                </div>
              </q-item-section>
            </q-item>
          </q-list>
          <div v-else-if="!wallLoading" class="text-body2 text-grey-7">{{ $t("profile.wallEmpty") }}</div>
          <q-inner-loading :showing="wallLoading" />

          <q-btn
            v-if="nextUrl"
            flat
            color="primary"
            class="q-mt-md"
            :label="$t('profile.loadMore')"
            :loading="loadingMore"
            @click="loadMore"
          />
        </div>
      </div>
    </template>
  </q-page>
</template>

<script setup lang="ts">
import { computed, ref, watch } from "vue";
import { useRoute, useRouter } from "vue-router";
import { useQuasar } from "quasar";
import { useI18n } from "vue-i18n";
import { api } from "@/api/client";
import { toRelativeApiPath } from "@/lib/apiUrl";
import { useAuthStore } from "@/stores/auth";
import type { Paginated, ProfilePublic, WallPost } from "@/types/profile";

const route = useRoute();
const router = useRouter();
const auth = useAuthStore();
const $q = useQuasar();
const { t, locale } = useI18n();

const userId = computed(() => Number(route.params.id));

const loadingProfile = ref(false);
const profileError = ref("");
const profile = ref<ProfilePublic | null>(null);

const wallLoading = ref(false);
const wallError = ref("");
const posts = ref<WallPost[]>([]);
const nextUrl = ref<string | null>(null);
const loadingMore = ref(false);
const posting = ref(false);

const newPostBody = ref("");
const editingId = ref<number | null>(null);
const editBody = ref("");
const startingChat = ref(false);

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

function canEditPost(p: WallPost): boolean {
  return auth.isAuthenticated && auth.user?.id === p.author_id;
}

async function loadProfile() {
  loadingProfile.value = true;
  profileError.value = "";
  profile.value = null;
  try {
    const { data } = await api.get<ProfilePublic>(`/profiles/${userId.value}/`);
    profile.value = data;
  } catch {
    profileError.value = t("profile.notFound");
  } finally {
    loadingProfile.value = false;
  }
}

async function loadWall(reset: boolean) {
  if (reset) {
    posts.value = [];
    nextUrl.value = null;
  }
  wallLoading.value = true;
  wallError.value = "";
  try {
    const { data } = await api.get<Paginated<WallPost>>(`/walls/${userId.value}/posts/`);
    posts.value = reset ? data.results : [...posts.value, ...data.results];
    nextUrl.value = data.next;
  } catch {
    wallError.value = t("profile.wallUnavailable");
    posts.value = [];
    nextUrl.value = null;
  } finally {
    wallLoading.value = false;
  }
}

async function loadMore() {
  if (!nextUrl.value) return;
  loadingMore.value = true;
  try {
    const path = toRelativeApiPath(nextUrl.value);
    const { data } = await api.get<Paginated<WallPost>>(path);
    posts.value.push(...data.results);
    nextUrl.value = data.next;
  } finally {
    loadingMore.value = false;
  }
}

async function submitPost() {
  if (!newPostBody.value.trim()) return;
  posting.value = true;
  try {
    const { data } = await api.post<WallPost>(`/walls/${userId.value}/posts/`, {
      body: newPostBody.value.trim(),
    });
    posts.value.unshift(data);
    newPostBody.value = "";
  } finally {
    posting.value = false;
  }
}

function startEdit(p: WallPost) {
  editingId.value = p.id;
  editBody.value = p.body;
}

function cancelEdit() {
  editingId.value = null;
  editBody.value = "";
}

async function saveEdit(postId: number) {
  const { data } = await api.patch<WallPost>(`/walls/posts/${postId}/`, { body: editBody.value });
  const i = posts.value.findIndex((x) => x.id === postId);
  if (i >= 0) posts.value[i] = data;
  cancelEdit();
}

async function startDirect() {
  startingChat.value = true;
  try {
    const { data } = await api.post<{ id: number }>("/messaging/conversations/", {
      participant_id: userId.value,
    });
    await router.push({ name: "conversation", params: { id: String(data.id) } });
  } catch {
    $q.notify({ type: "negative", message: t("profile.chatStartFailed") });
  } finally {
    startingChat.value = false;
  }
}

function confirmDelete(p: WallPost) {
  $q.dialog({
    title: t("profile.deletePostTitle"),
    message: t("profile.deletePostMessage"),
    cancel: true,
    persistent: true,
  }).onOk(async () => {
    await api.delete(`/walls/posts/${p.id}/`);
    posts.value = posts.value.filter((x) => x.id !== p.id);
  });
}

watch(
  userId,
  (id) => {
    if (!Number.isFinite(id) || id < 1) {
      profileError.value = t("profile.notFound");
      return;
    }
    void loadProfile();
    void loadWall(true);
  },
  { immediate: true }
);
</script>
