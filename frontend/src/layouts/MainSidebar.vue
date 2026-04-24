<template>
  <q-drawer
    v-model="open"
    show-if-above
    bordered
    :breakpoint="1024"
    :width="260"
    behavior="default"
  >
    <q-scroll-area class="fit">
      <q-list padding>
        <q-item
          v-for="item in items"
          :key="item.to"
          v-ripple
          clickable
          :to="item.to"
          :exact="item.exact"
          active-class="bg-primary text-white"
        >
          <q-item-section avatar>
            <q-icon :name="item.icon" />
          </q-item-section>
          <q-item-section>{{ $t(item.labelKey) }}</q-item-section>
        </q-item>
      </q-list>
    </q-scroll-area>
  </q-drawer>
</template>

<script setup lang="ts">
import { watch } from "vue";
import { useQuasar } from "quasar";
import { useRoute } from "vue-router";

const open = defineModel<boolean>({ required: true });

const $q = useQuasar();
const route = useRoute();

const items = [
  { to: "/", icon: "home", labelKey: "nav.home", exact: true },
  { to: "/dashboard", icon: "dashboard", labelKey: "nav.dashboard", exact: false },
] as const;

watch(
  () => route.fullPath,
  () => {
    if ($q.screen.lt.md) {
      open.value = false;
    }
  }
);
</script>
