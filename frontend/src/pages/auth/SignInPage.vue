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
      <q-banner
        v-if="showCaptcha && !hcaptchaSitekey"
        rounded
        dense
        class="bg-warning text-dark q-mt-sm"
      >
        {{ $t("auth.captchaMissingSitekey") }}
      </q-banner>
      <div v-if="showCaptcha && hcaptchaSitekey" class="q-mt-md">
        <div class="text-caption q-mb-xs">{{ $t("auth.captchaHint") }}</div>
        <VueHcaptcha
          ref="hcaptchaRef"
          :sitekey="hcaptchaSitekey"
          :language="hcaptchaLanguage"
          @verify="onCaptchaVerify"
          @expired="onCaptchaExpired"
        />
      </div>
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
import { isAxiosError } from "axios";
import { computed, nextTick, ref, watch } from "vue";
import { useI18n } from "vue-i18n";
import { useRoute, useRouter } from "vue-router";
import VueHcaptcha from "@hcaptcha/vue3-hcaptcha";
import { useAuthStore } from "@/stores/auth";

const email = ref("");
const password = ref("");
const loading = ref(false);
const errorMsg = ref("");
const showCaptcha = ref(false);
const captchaToken = ref("");
const hcaptchaRef = ref<{ reset?: () => void } | null>(null);

const { locale, t } = useI18n();
const auth = useAuthStore();
const router = useRouter();
const route = useRoute();

const hcaptchaSitekey = computed(() => (import.meta.env.VITE_HCAPTCHA_SITEKEY || "").trim());
const hcaptchaLanguage = computed(() => (locale.value.startsWith("ru") ? "ru" : "en"));

const required = (v: string) => (v && v.length > 0) || "";

function resetCaptchaWidget() {
  captchaToken.value = "";
  nextTick(() => hcaptchaRef.value?.reset?.());
}

watch(email, () => {
  showCaptcha.value = false;
  captchaToken.value = "";
});

watch(password, () => {
  if (showCaptcha.value) {
    resetCaptchaWidget();
  }
});

function apiErrorMessage(data: unknown): string {
  if (!data || typeof data !== "object") return "";
  const d = data as { detail?: unknown; non_field_errors?: string[] };
  if (typeof d.detail === "string") return d.detail;
  if (Array.isArray(d.detail) && typeof d.detail[0] === "string") return d.detail[0];
  if (d.non_field_errors?.length) return d.non_field_errors[0];
  return "";
}

function onCaptchaVerify(token: string) {
  captchaToken.value = token;
}

function onCaptchaExpired() {
  resetCaptchaWidget();
}

async function onSubmit() {
  errorMsg.value = "";
  if (showCaptcha.value && hcaptchaSitekey.value && !captchaToken.value) {
    errorMsg.value = t("auth.captchaSolveFirst");
    return;
  }
  loading.value = true;
  try {
    const token = showCaptcha.value && hcaptchaSitekey.value ? captchaToken.value : null;
    await auth.login(email.value.trim(), password.value, token);
    const redirect = typeof route.query.redirect === "string" ? route.query.redirect : "/";
    await router.replace(redirect || "/");
  } catch (e: unknown) {
    if (!isAxiosError(e) || !e.response?.data) {
      errorMsg.value = String(e);
      return;
    }
    const data = e.response.data as { code?: string; detail?: unknown; non_field_errors?: string[] };
    if (data.code === "captcha_required") {
      showCaptcha.value = true;
      errorMsg.value = apiErrorMessage(data) || t("auth.captchaHint");
      resetCaptchaWidget();
      return;
    }
    errorMsg.value = apiErrorMessage(data) || t("auth.signInFailed");
    if (showCaptcha.value && hcaptchaSitekey.value) {
      resetCaptchaWidget();
    }
  } finally {
    loading.value = false;
  }
}
</script>
