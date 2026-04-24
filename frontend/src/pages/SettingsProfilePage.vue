<template>
  <q-page padding>
    <div class="text-h6 q-mb-md">{{ $t("settings.profileTitle") }}</div>
    <q-linear-progress v-if="loading" indeterminate color="primary" class="q-mb-md" />
    <q-banner v-if="loadError" rounded dense class="bg-negative text-white q-mb-md">{{ loadError }}</q-banner>

    <q-form v-if="!loading && !loadError" class="q-gutter-md" style="max-width: 560px" @submit.prevent="onSave">
      <q-input v-model="form.bio" outlined type="textarea" autogrow :label="$t('settings.bio')" />
      <q-input v-model="form.avatar" outlined :label="$t('settings.avatarUrl')" />
      <q-select
        v-model="form.locale"
        outlined
        emit-value
        map-options
        :options="localeOptions"
        :label="$t('settings.locale')"
      />
      <q-select
        v-model="form.privacy"
        outlined
        emit-value
        map-options
        :options="privacyOptions"
        :label="$t('settings.privacy')"
      />
      <q-input v-model="form.default_landing" outlined :label="$t('settings.defaultLanding')" />
      <q-btn color="primary" type="submit" :loading="saving" :label="$t('settings.save')" />
      <q-banner v-if="savedOk" rounded dense class="bg-positive text-white">{{ $t("settings.saved") }}</q-banner>
    </q-form>
  </q-page>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref } from "vue";
import { useI18n } from "vue-i18n";
import { api } from "@/api/client";
import type { ProfileMe } from "@/types/profile";

const { t } = useI18n();

const loading = ref(true);
const saving = ref(false);
const loadError = ref("");
const savedOk = ref(false);

const form = reactive({
  bio: "",
  avatar: "",
  locale: "ru",
  privacy: "public" as "public" | "private",
  default_landing: "",
});

const localeOptions = [
  { label: "Русский", value: "ru" },
  { label: "English", value: "en" },
];

const privacyOptions = computed(() => [
  { label: t("settings.privacyPublic"), value: "public" },
  { label: t("settings.privacyPrivate"), value: "private" },
]);

async function fetchMe() {
  loading.value = true;
  loadError.value = "";
  try {
    const { data } = await api.get<ProfileMe>("/profiles/me/");
    form.bio = data.bio || "";
    form.avatar = data.avatar || "";
    form.locale = data.locale || "ru";
    form.privacy = data.privacy === "private" ? "private" : "public";
    form.default_landing = data.default_landing || "";
  } catch (e: unknown) {
    loadError.value = String(e);
  } finally {
    loading.value = false;
  }
}

async function onSave() {
  savedOk.value = false;
  saving.value = true;
  try {
    await api.patch("/profiles/me/", {
      bio: form.bio,
      avatar: form.avatar,
      locale: form.locale,
      privacy: form.privacy,
      default_landing: form.default_landing,
    });
    savedOk.value = true;
    window.setTimeout(() => {
      savedOk.value = false;
    }, 4000);
  } finally {
    saving.value = false;
  }
}

onMounted(fetchMe);
</script>
