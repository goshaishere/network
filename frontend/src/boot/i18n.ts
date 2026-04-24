import { createI18n } from "vue-i18n";
import ru from "@/i18n/ru-RU";
import en from "@/i18n/en-US";

export const i18n = createI18n({
  legacy: false,
  locale: "ru",
  fallbackLocale: "en",
  messages: { ru, en },
  globalInjection: true,
});
