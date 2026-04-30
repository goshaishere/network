import type { AuthUser } from "@/stores/auth";

/** Доступ к маршрутам «внутренний контур» (штат или staff), не партнёр без staff. */
export function canAccessInternalRoute(user: AuthUser | null | undefined): boolean {
  if (!user) return false;
  return Boolean(user.is_staff || (user.is_employee && user.employment_kind === "internal"));
}
