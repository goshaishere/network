import { createApp } from "vue";
import axios from "axios";
import { Dark, Quasar } from "quasar";
import quasarLang from "quasar/lang/ru";
import { createPinia } from "pinia";
import "@quasar/extras/material-icons/material-icons.css";
import "quasar/src/css/index.sass";
import App from "./App.vue";
import router from "./router";
import { i18n } from "./boot/i18n";
import { api } from "./api/client";
import { useAuthStore } from "./stores/auth";
import "./css/app.scss";

Dark.set(typeof localStorage !== "undefined" && localStorage.getItem("network-dark") === "1");
const savedLocale = typeof localStorage !== "undefined" ? localStorage.getItem("network-locale") : null;
if (savedLocale === "en" || savedLocale === "ru") {
  i18n.global.locale.value = savedLocale;
}

const app = createApp(App);
const pinia = createPinia();
app.use(pinia);
app.use(Quasar, {
  plugins: { Dark },
  lang: quasarLang,
});
app.use(i18n);
app.use(router);

const authStore = useAuthStore();
authStore.hydrateFromStorage();

api.interceptors.request.use((config) => {
  const a = useAuthStore();
  if (a.accessToken) {
    config.headers.Authorization = `Bearer ${a.accessToken}`;
  }
  return config;
});

let refreshing = false;
api.interceptors.response.use(
  (res) => res,
  async (error) => {
    const original = error.config as typeof error.config & { _retry?: boolean };
    if (!original || original._retry) {
      return Promise.reject(error);
    }
    if (error.response?.status !== 401) {
      return Promise.reject(error);
    }
    if (String(original.url || "").includes("/auth/token/refresh/")) {
      return Promise.reject(error);
    }
    const a = useAuthStore();
    if (!a.refreshToken) {
      return Promise.reject(error);
    }
    original._retry = true;
    if (refreshing) {
      return Promise.reject(error);
    }
    refreshing = true;
    try {
      const base = api.defaults.baseURL || "";
      const { data } = await axios.post<{ access: string; refresh?: string }>(
        `${base}/auth/token/refresh/`,
        { refresh: a.refreshToken }
      );
      a.applyTokenRefresh({ access: data.access, refresh: data.refresh });
      original.headers.Authorization = `Bearer ${data.access}`;
      refreshing = false;
      return api(original);
    } catch {
      refreshing = false;
      a.clearSession();
      return Promise.reject(error);
    }
  }
);

app.mount("#app");
