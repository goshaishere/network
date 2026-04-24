<template>
  <div>
    <div class="text-subtitle1 q-mb-md">{{ $t("auth.resetConfirmTitle") }}</div>
    <q-form @submit="onSubmit">
      <q-input
        v-model="newPassword"
        outlined
        type="password"
        :label="$t('auth.newPassword')"
        lazy-rules
        :rules="[required, min8]"
      />
      <q-input
        v-model="newPasswordConfirm"
        class="q-mt-sm"
        outlined
        type="password"
        :label="$t('auth.passwordConfirm')"
        lazy-rules
        :rules="[required, matchPwd]"
      />
      <q-banner v-if="errorMsg" rounded dense class="bg-negative text-white q-mt-sm">{{ errorMsg }}</q-banner>
      <q-btn class="full-width q-mt-md" color="primary" type="submit" :loading="loading" :label="$t('auth.savePassword')" />
    </q-form>
    <div class="q-mt-md text-center text-caption">
      <router-link class="text-primary" :to="{ name: 'auth-login' }">{{ $t("auth.backToLogin") }}</router-link>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from "vue";
import { useI18n } from "vue-i18n";
import { useRoute, useRouter } from "vue-router";
import { useAuthStore } from "@/stores/auth";

const uid = ref("");
const token = ref("");
const newPassword = ref("");
const newPasswordConfirm = ref("");
const loading = ref(false);
const errorMsg = ref("");

const auth = useAuthStore();
const route = useRoute();
const router = useRouter();
const { t } = useI18n();

const required = (v: string) => (v && v.length > 0) || "";
const min8 = (v: string) => (v && v.length >= 8) || "";
const matchPwd = (v: string) => v === newPassword.value || "";

onMounted(() => {
  uid.value = typeof route.query.uid === "string" ? route.query.uid : "";
  token.value = typeof route.query.token === "string" ? route.query.token : "";
  if (!uid.value || !token.value) {
    errorMsg.value = t("auth.invalidResetLink");
  }
});

async function onSubmit() {
  errorMsg.value = "";
  if (!uid.value || !token.value) {
    errorMsg.value = "Invalid link";
    return;
  }
  loading.value = true;
  try {
    await auth.confirmPasswordReset({
      uid: uid.value,
      token: token.value,
      new_password: newPassword.value,
      new_password_confirm: newPasswordConfirm.value,
    });
    await router.replace({ name: "auth-login" });
  } catch (e: unknown) {
    const err = e as { response?: { data?: { detail?: string } } };
    errorMsg.value = err.response?.data?.detail || String(e);
  } finally {
    loading.value = false;
  }
}
</script>
