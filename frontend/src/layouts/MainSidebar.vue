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
          v-for="item in mainLinks"
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

        <q-separator class="q-my-sm" />

        <q-item v-if="!auth.isAuthenticated" v-ripple clickable :to="{ name: 'auth-login' }">
          <q-item-section avatar>
            <q-icon name="login" />
          </q-item-section>
          <q-item-section>{{ $t("nav.signIn") }}</q-item-section>
        </q-item>
        <q-item v-if="!auth.isAuthenticated" v-ripple clickable :to="{ name: 'auth-register' }">
          <q-item-section avatar>
            <q-icon name="person_add" />
          </q-item-section>
          <q-item-section>{{ $t("nav.signUp") }}</q-item-section>
        </q-item>

        <template v-else>
          <q-item v-ripple clickable :to="{ name: 'settings-profile' }">
            <q-item-section avatar>
              <q-icon name="manage_accounts" />
            </q-item-section>
            <q-item-section>{{ $t("nav.settings") }}</q-item-section>
          </q-item>
          <q-item v-if="auth.user?.is_staff" v-ripple clickable :to="{ name: 'console' }">
            <q-item-section avatar>
              <q-icon name="admin_panel_settings" />
            </q-item-section>
            <q-item-section>{{ $t("nav.console") }}</q-item-section>
          </q-item>
          <q-item v-ripple clickable @click="onLogout">
            <q-item-section avatar>
              <q-icon name="logout" />
            </q-item-section>
            <q-item-section>{{ $t("nav.signOut") }}</q-item-section>
          </q-item>
        </template>
      </q-list>
    </q-scroll-area>
  </q-drawer>
</template>

<script setup lang="ts">
import { computed, watch } from "vue";
import { useQuasar } from "quasar";
import { useRoute, useRouter } from "vue-router";
import { useAuthStore } from "@/stores/auth";

const open = defineModel<boolean>({ required: true });

const $q = useQuasar();
const route = useRoute();
const router = useRouter();
const auth = useAuthStore();

const mainLinks = computed(() => {
  const links = [
    { to: "/", icon: "home", labelKey: "nav.home", exact: true },
    { to: "/dashboard", icon: "dashboard", labelKey: "nav.dashboard", exact: false },
    { to: "/communities", icon: "groups", labelKey: "nav.communities", exact: false },
    { to: "/messages", icon: "chat", labelKey: "nav.messages", exact: false },
    { to: "/work", icon: "work", labelKey: "nav.work", exact: false },
  ];
  if (auth.isAuthenticated && auth.user) {
    links.push({
      to: `/profile/${auth.user.id}`,
      icon: "person",
      labelKey: "nav.profile",
      exact: false,
    });
  }
  return links;
});

watch(
  () => route.fullPath,
  () => {
    if ($q.screen.lt.md) {
      open.value = false;
    }
  }
);

async function onLogout() {
  await auth.logout();
  if (route.matched.some((r) => r.meta.requiresAuth)) {
    await router.replace({ name: "home" });
  }
  open.value = false;
}
</script>
