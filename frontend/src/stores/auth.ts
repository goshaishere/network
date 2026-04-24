import { defineStore } from "pinia";
import { computed, ref } from "vue";
import { api } from "@/api/client";

const LS_ACCESS = "network_access";
const LS_REFRESH = "network_refresh";
const LS_USER = "network_user";

export interface AuthUser {
  id: number;
  email: string;
  display_name: string;
  is_staff: boolean;
  is_employee: boolean;
  employment_kind: "" | "internal" | "partner";
}

export const useAuthStore = defineStore("auth", () => {
  const accessToken = ref<string | null>(null);
  const refreshToken = ref<string | null>(null);
  const user = ref<AuthUser | null>(null);
  /** Увеличивается при смене access (логин, refresh) — для переподключения WS и т.п. */
  const tokenGeneration = ref(0);

  const isAuthenticated = computed(() => Boolean(accessToken.value && user.value));

  function bumpTokenGeneration() {
    tokenGeneration.value += 1;
  }

  function hydrateFromStorage() {
    accessToken.value = localStorage.getItem(LS_ACCESS);
    refreshToken.value = localStorage.getItem(LS_REFRESH);
    const raw = localStorage.getItem(LS_USER);
    if (!raw) {
      user.value = null;
      return;
    }
    const u = JSON.parse(raw) as Partial<AuthUser>;
    if (typeof u.is_employee !== "boolean") {
      u.is_employee = false;
    }
    if (u.employment_kind !== "internal" && u.employment_kind !== "partner") {
      u.employment_kind = "";
    }
    user.value = u as AuthUser;
  }

  function persist() {
    if (accessToken.value) localStorage.setItem(LS_ACCESS, accessToken.value);
    else localStorage.removeItem(LS_ACCESS);
    if (refreshToken.value) localStorage.setItem(LS_REFRESH, refreshToken.value);
    else localStorage.removeItem(LS_REFRESH);
    if (user.value) localStorage.setItem(LS_USER, JSON.stringify(user.value));
    else localStorage.removeItem(LS_USER);
  }

  function setSession(access: string, refresh: string, u: AuthUser) {
    accessToken.value = access;
    refreshToken.value = refresh;
    user.value = u;
    persist();
    bumpTokenGeneration();
  }

  function setAccess(access: string) {
    accessToken.value = access;
    persist();
    bumpTokenGeneration();
  }

  function applyTokenRefresh(data: { access: string; refresh?: string }) {
    accessToken.value = data.access;
    if (data.refresh) {
      refreshToken.value = data.refresh;
    }
    persist();
    bumpTokenGeneration();
  }

  function clearSession() {
    accessToken.value = null;
    refreshToken.value = null;
    user.value = null;
    persist();
    bumpTokenGeneration();
  }

  async function register(payload: {
    email: string;
    display_name: string;
    password: string;
    password_confirm: string;
  }) {
    const { data } = await api.post<{
      user: AuthUser;
      access: string;
      refresh: string;
    }>("/auth/register/", payload);
    setSession(data.access, data.refresh, data.user);
  }

  async function login(email: string, password: string, captchaToken?: string | null) {
    const body: Record<string, string> = { email, password };
    if (captchaToken) {
      body.captcha_token = captchaToken;
    }
    const { data } = await api.post<{ access: string; refresh: string }>("/auth/login/", body);
    accessToken.value = data.access;
    refreshToken.value = data.refresh;
    localStorage.setItem(LS_ACCESS, data.access);
    localStorage.setItem(LS_REFRESH, data.refresh);
    bumpTokenGeneration();
    await fetchMe();
  }

  async function fetchMe() {
    const { data } = await api.get<AuthUser>("/auth/me/");
    user.value = data;
    persist();
  }

  async function logout() {
    const rt = refreshToken.value;
    try {
      if (rt) await api.post("/auth/logout/", { refresh: rt });
    } catch {
      /* ignore */
    }
    clearSession();
  }

  async function requestPasswordReset(email: string) {
    await api.post("/auth/password/reset/request/", { email });
  }

  async function confirmPasswordReset(payload: {
    uid: string;
    token: string;
    new_password: string;
    new_password_confirm: string;
  }) {
    await api.post("/auth/password/reset/confirm/", payload);
  }

  return {
    accessToken,
    refreshToken,
    user,
    tokenGeneration,
    isAuthenticated,
    hydrateFromStorage,
    setSession,
    setAccess,
    applyTokenRefresh,
    clearSession,
    register,
    login,
    fetchMe,
    logout,
    requestPasswordReset,
    confirmPasswordReset,
  };
});
