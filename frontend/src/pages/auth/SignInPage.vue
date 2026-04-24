<template>
  <div>
    <div class="text-subtitle1 q-mb-md">{{ $t("auth.signInTitle") }}</div>
    <q-form @submit="onSubmit">
      <q-input v-model="email" outlined type="email" :label="$t('auth.email')" lazy-rules :rules="[required]" />
      <q-input
        v-model="password"
        class="q-mt-sm"
        outlined
        type="password"
        :label="$t('auth.password')"
        lazy-rules
        :rules="[required]"
      />
      <q-banner v-if="errorMsg" rounded dense class="bg-negative text-white q-mt-sm">{{ errorMsg }}</q-banner>
      <q-btn class="full-width q-mt-md" color="primary" type="submit" :loading="loading" :label="$t('auth.signIn')" />
    </q-form>
    <div class="row justify-between q-mt-md text-caption">
      <router-link class="text-primary" :to="{ name: 'auth-register' }">{{ $t("auth.toRegister") }}</router-link>
      <router-link class="text-primary" :to="{ name: 'auth-password-reset' }">{{ $t("auth.forgotPassword") }}</router-link>
    </div>
    <div class="q-mt-md text-center">
      <router-link class="text-grey-7" to="/">{{ $t("auth.backHome") }}</router-link>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from "vue";
import { useRoute, useRouter } from "vue-router";
import { useAuthStore } from "@/stores/auth";

const email = ref("");
const password = ref("");
const loading = ref(false);
const errorMsg = ref("");

const auth = useAuthStore();
const router = useRouter();
const route = useRoute();

const required = (v: string) => (v && v.length > 0) || "";

async function onSubmit() {
  errorMsg.value = "";
  loading.value = true;
  try {
    await auth.login(email.value.trim(), password.value);
    const redirect = typeof route.query.redirect === "string" ? route.query.redirect : "/";
    await router.replace(redirect || "/");
  } catch (e: unknown) {
    const err = e as { response?: { data?: { detail?: string; non_field_errors?: string[] } } };
    const d = err.response?.data;
    errorMsg.value =
      (typeof d?.detail === "string" && d.detail) ||
      d?.non_field_errors?.[0] ||
      String(e);
  } finally {
    loading.value = false;
  }
}
</script>
