import type { Router } from "vue-router";
import { i18n } from "@/boot/i18n";
import { useAuthStore } from "@/stores/auth";

export function setupRouterGuards(_router: Router) {
  _router.beforeEach(async (to, _from, next) => {
    const auth = useAuthStore();

    if (auth.accessToken && !auth.user) {
      try {
        await auth.fetchMe();
      } catch {
        auth.clearSession();
      }
    }

    const requiresAuth = to.matched.some((r) => r.meta.requiresAuth);
    const guestOnly = to.matched.some((r) => r.meta.guestOnly);
    const requiresStaff = to.matched.some((r) => r.meta.requiresStaff);
    const requiresEmployee = to.matched.some((r) => r.meta.requiresEmployee);

    if (requiresAuth && !auth.isAuthenticated) {
      next({ name: "auth-login", query: { redirect: to.fullPath } });
      return;
    }

    if (guestOnly && auth.isAuthenticated) {
      next({ name: "home" });
      return;
    }

    if (requiresStaff && !auth.user?.is_staff) {
      next({ name: "home" });
      return;
    }

    if (requiresEmployee && auth.isAuthenticated) {
      const u = auth.user;
      if (!u?.is_staff && !u?.is_employee) {
        next({ name: "home" });
        return;
      }
    }

    const leaf = to.matched[to.matched.length - 1];
    const titleKey = leaf?.meta?.titleKey as string | undefined;
    if (titleKey) {
      document.title = `${i18n.global.t(titleKey)} · Network`;
    } else {
      document.title = "Network";
    }

    next();
  });
}
