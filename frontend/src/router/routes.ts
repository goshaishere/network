import type { RouteRecordRaw } from "vue-router";

const mainChildren: RouteRecordRaw[] = [
  {
    path: "",
    name: "home",
    component: () => import("@/pages/IndexPage.vue"),
    meta: { titleKey: "nav.home" },
  },
  {
    path: "dashboard",
    name: "dashboard",
    component: () => import("@/pages/PlaceholderPage.vue"),
    meta: {
      titleKey: "dashboard.stubTitle",
      stubBodyKey: "dashboard.stubBody",
      requiresAuth: true,
    },
  },
  {
    path: "communities",
    name: "communities",
    component: () => import("@/pages/PlaceholderPage.vue"),
    meta: {
      titleKey: "communities.stubTitle",
      stubBodyKey: "communities.stubBody",
    },
  },
  {
    path: "communities/:slug",
    name: "community-detail",
    component: () => import("@/pages/PlaceholderPage.vue"),
    meta: {
      titleKey: "communities.detailTitle",
      stubBodyKey: "communities.stubBody",
    },
  },
  {
    path: "messages",
    name: "messages",
    component: () => import("@/pages/PlaceholderPage.vue"),
    meta: {
      titleKey: "messages.stubTitle",
      stubBodyKey: "messages.stubBody",
      requiresAuth: true,
    },
  },
  {
    path: "messages/:id",
    name: "conversation",
    component: () => import("@/pages/PlaceholderPage.vue"),
    meta: {
      titleKey: "messages.chatTitle",
      stubBodyKey: "messages.stubBody",
      requiresAuth: true,
    },
  },
  {
    path: "work",
    name: "work",
    component: () => import("@/pages/PlaceholderPage.vue"),
    meta: {
      titleKey: "work.stubTitle",
      stubBodyKey: "work.stubBody",
      requiresAuth: true,
    },
  },
  {
    path: "console",
    name: "console",
    component: () => import("@/pages/PlaceholderPage.vue"),
    meta: {
      titleKey: "console.stubTitle",
      stubBodyKey: "console.stubBody",
      requiresAuth: true,
      requiresStaff: true,
    },
  },
  {
    path: "settings/profile",
    name: "settings-profile",
    component: () => import("@/pages/PlaceholderPage.vue"),
    meta: {
      titleKey: "settings.profileTitle",
      stubBodyKey: "settings.stubBody",
      requiresAuth: true,
    },
  },
  {
    path: "profile/:id",
    name: "user-profile",
    component: () => import("@/pages/PlaceholderPage.vue"),
    meta: {
      titleKey: "profile.stubTitle",
      stubBodyKey: "profile.stubBody",
    },
  },
];

const routes: RouteRecordRaw[] = [
  {
    path: "/",
    component: () => import("@/layouts/MainLayout.vue"),
    children: mainChildren,
  },
  {
    path: "/auth",
    component: () => import("@/layouts/AuthLayout.vue"),
    meta: { guestOnly: true },
    children: [
      {
        path: "login",
        name: "auth-login",
        component: () => import("@/pages/auth/SignInPage.vue"),
        meta: { titleKey: "auth.signInTitle", guestOnly: true },
      },
      {
        path: "register",
        name: "auth-register",
        component: () => import("@/pages/auth/SignUpPage.vue"),
        meta: { titleKey: "auth.signUpTitle", guestOnly: true },
      },
      {
        path: "password-reset",
        name: "auth-password-reset",
        component: () => import("@/pages/auth/PasswordResetRequestPage.vue"),
        meta: { titleKey: "auth.resetRequestTitle", guestOnly: true },
      },
      {
        path: "password-reset/confirm",
        name: "auth-password-reset-confirm",
        component: () => import("@/pages/auth/PasswordResetConfirmPage.vue"),
        meta: { titleKey: "auth.resetConfirmTitle", guestOnly: true },
      },
    ],
  },
  {
    path: "/:pathMatch(.*)*",
    name: "not-found",
    component: () => import("@/pages/ErrorNotFound.vue"),
  },
];

export default routes;
