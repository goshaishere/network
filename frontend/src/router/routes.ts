import type { RouteRecordRaw } from "vue-router";

const routes: RouteRecordRaw[] = [
  {
    path: "/",
    component: () => import("@/layouts/MainLayout.vue"),
    children: [
      {
        path: "",
        name: "home",
        component: () => import("@/pages/IndexPage.vue"),
        meta: { title: "Network" },
      },
      {
        path: "dashboard",
        name: "dashboard",
        component: () => import("@/pages/DashboardStubPage.vue"),
        meta: { title: "Dashboard" },
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
