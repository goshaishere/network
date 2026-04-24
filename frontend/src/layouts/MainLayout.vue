<template>
  <q-layout view="hHh Lpr fFf">
    <q-header elevated class="bg-primary text-white">
      <q-toolbar>
        <q-btn
          flat
          dense
          round
          icon="menu"
          aria-label="Menu"
          class="lt-md"
          @click="drawerOpen = !drawerOpen"
        />
        <q-toolbar-title>{{ $t("appTitle") }}</q-toolbar-title>
        <q-space />
        <q-btn-toggle
          v-model="localeModel"
          spread
          no-caps
          unelevated
          toggle-color="white"
          color="primary"
          text-color="white"
          :options="[
            { label: 'RU', value: 'ru' },
            { label: 'EN', value: 'en' },
          ]"
        />
        <q-toggle v-model="darkModel" color="white" class="q-ml-sm" icon="dark_mode" />
      </q-toolbar>
    </q-header>

    <MainSidebar v-model="drawerOpen" />

    <q-page-container>
      <router-view />
    </q-page-container>
  </q-layout>
</template>

<script setup lang="ts">
import { computed, ref } from "vue";
import { useQuasar } from "quasar";
import { useI18n } from "vue-i18n";
import MainSidebar from "./MainSidebar.vue";

const drawerOpen = ref(false);
const $q = useQuasar();
const { locale } = useI18n();

const localeModel = computed({
  get: () => (locale.value === "en" ? "en" : "ru"),
  set: (v: string) => {
    const next = v === "en" ? "en" : "ru";
    locale.value = next;
    localStorage.setItem("network-locale", next);
  },
});

const darkModel = computed({
  get: () => $q.dark.isActive,
  set: (on: boolean) => {
    $q.dark.set(on);
    localStorage.setItem("network-dark", on ? "1" : "0");
  },
});
</script>
