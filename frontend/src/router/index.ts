import { createRouter, createWebHistory } from "vue-router";
import { setupRouterGuards } from "./guards";
import routes from "./routes";

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
});

setupRouterGuards(router);

export default router;
