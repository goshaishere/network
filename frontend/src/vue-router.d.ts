import "vue-router";

declare module "vue-router" {
  interface RouteMeta {
    requiresAuth?: boolean;
    guestOnly?: boolean;
    requiresStaff?: boolean;
    titleKey?: string;
    stubBodyKey?: string;
  }
}
