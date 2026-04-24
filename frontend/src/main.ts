import { createApp } from "vue";
import { Dark, Quasar } from "quasar";
import quasarLang from "quasar/lang/ru";
import { createPinia } from "pinia";
import "@quasar/extras/material-icons/material-icons.css";
import "quasar/src/css/index.sass";
import App from "./App.vue";
import router from "./router";
import { i18n } from "./boot/i18n";
import "./css/app.scss";

Dark.set(typeof localStorage !== "undefined" && localStorage.getItem("network-dark") === "1");
const savedLocale = typeof localStorage !== "undefined" ? localStorage.getItem("network-locale") : null;
if (savedLocale === "en" || savedLocale === "ru") {
  i18n.global.locale.value = savedLocale;
}

const app = createApp(App);
app.use(createPinia());
app.use(Quasar, {
  plugins: { Dark },
  lang: quasarLang,
});
app.use(i18n);
app.use(router);
app.mount("#app");
