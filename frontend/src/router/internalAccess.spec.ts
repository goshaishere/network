import { describe, expect, it } from "vitest";
import { canAccessInternalRoute } from "./internalAccess";
import type { AuthUser } from "@/stores/auth";

function u(partial: Partial<AuthUser> & Pick<AuthUser, "id" | "email">): AuthUser {
  return {
    display_name: "",
    is_staff: false,
    is_employee: false,
    employment_kind: "",
    ...partial,
  } as AuthUser;
}

describe("canAccessInternalRoute", () => {
  it("allows staff", () => {
    expect(canAccessInternalRoute(u({ id: 1, email: "a@a", is_staff: true }))).toBe(true);
  });
  it("allows internal employee", () => {
    expect(
      canAccessInternalRoute(
        u({ id: 1, email: "a@a", is_employee: true, employment_kind: "internal" })
      )
    ).toBe(true);
  });
  it("denies partner employee", () => {
    expect(
      canAccessInternalRoute(
        u({ id: 1, email: "a@a", is_employee: true, employment_kind: "partner" })
      )
    ).toBe(false);
  });
  it("denies plain user", () => {
    expect(canAccessInternalRoute(u({ id: 1, email: "a@a" }))).toBe(false);
  });
  it("denies null", () => {
    expect(canAccessInternalRoute(null)).toBe(false);
  });
});
