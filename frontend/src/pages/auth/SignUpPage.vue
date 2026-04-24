<template>
  <div>
    <div class="text-subtitle1 q-mb-md">{{ $t("auth.signUpTitle") }}</div>
    <q-form @submit="onSubmit">
      <q-input v-model="email" outlined type="email" :label="$t('auth.email')" lazy-rules :rules="[required]" />
      <q-input v-model="displayName" class="q-mt-sm" outlined :label="$t('auth.displayName')" />
      <q-input
        v-model="password"
        class="q-mt-sm"
        outlined
        type="password"
        :label="$t('auth.password')"
        lazy-rules
        :rules="[required, min8]"
      />
      <q-input
        v-model="passwordConfirm"
        class="q-mt-sm"
        outlined
        type="password"
        :label="$t('auth.passwordConfirm')"
        lazy-rules
        :rules="[required, matchPwd]"
      />
      <q-banner v-if="errorMsg" rounded dense class="bg-negative text-white q-mt-sm">{{ errorMsg }}</q-banner>
      <q-btn class="full-width q-mt-md" color="primary" type="submit" :loading="loading" :label="$t('auth.signUp')" />
    </q-form>
    <div class="q-mt-md text-center text-caption">
      <router-link class="text-primary" :to="{ name: 'auth-login' }">{{ $t("auth.haveAccount") }}</router-link>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from "vue";
import { useRouter } from "vue-router";
import { useAuthStore } from "@/stores/auth";

const email = ref("");
const displayName = ref("");
const password = ref("");
const passwordConfirm = ref("");
const loading = ref(false);
const errorMsg = ref("");

const auth = useAuthStore();
const router = useRouter();

const required = (v: string) => (v && v.length > 0) || "";
const min8 = (v: string) => (v && v.length >= 8) || "";
const matchPwd = (v: string) => v === password.value || "";

function flattenErrors(data: unknown): string {
  if (typeof data === "object" && data !== null) {
    const o = data as Record<string, string[] | string>;
    for (const k of Object.keys(o)) {
      const v = o[k];
      if (Array.isArray(v) && v[0]) return `${k}: ${v[0]}`;
      if (typeof v === "string") return v;
    }
  }
  return "";
}

async function onSubmit() {
  errorMsg.value = "";
  loading.value = true;
  try {
    await auth.register({
      email: email.value.trim(),
      display_name: displayName.value.trim(),
      password: password.value,
      password_confirm: passwordConfirm.value,
    });
    await router.replace("/");
  } catch (e: unknown) {
    const err = e as { response?: { data?: unknown } };
    const d = err.response?.data;
    errorMsg.value = flattenErrors(d) || String(e);
  } finally {
    loading.value = false;
  }
}
</script>
