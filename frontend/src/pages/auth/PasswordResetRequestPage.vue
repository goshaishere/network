<template>
  <div>
    <div class="text-subtitle1 q-mb-md">{{ $t("auth.resetRequestTitle") }}</div>
    <q-form @submit="onSubmit">
      <q-input v-model="email" outlined type="email" :label="$t('auth.email')" lazy-rules :rules="[required]" />
      <q-banner v-if="errorMsg" rounded dense class="bg-negative text-white q-mt-sm">{{ errorMsg }}</q-banner>
      <q-banner v-if="done" rounded dense class="bg-positive text-white q-mt-sm">{{ $t("auth.resetEmailSent") }}</q-banner>
      <q-btn
        class="full-width q-mt-md"
        color="primary"
        type="submit"
        :loading="loading"
        :disable="done"
        :label="$t('auth.sendResetLink')"
      />
    </q-form>
    <div class="q-mt-md text-center text-caption">
      <router-link class="text-primary" :to="{ name: 'auth-login' }">{{ $t("auth.backToLogin") }}</router-link>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from "vue";
import { useAuthStore } from "@/stores/auth";

const email = ref("");
const loading = ref(false);
const errorMsg = ref("");
const done = ref(false);

const auth = useAuthStore();
const required = (v: string) => (v && v.length > 0) || "";

async function onSubmit() {
  errorMsg.value = "";
  loading.value = true;
  try {
    await auth.requestPasswordReset(email.value.trim());
    done.value = true;
  } catch (e: unknown) {
    errorMsg.value = String(e);
  } finally {
    loading.value = false;
  }
}
</script>
