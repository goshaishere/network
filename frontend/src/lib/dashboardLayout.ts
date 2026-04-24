import type { DashboardLayoutPayload, DashboardWidget } from "@/types/profile";

function newId(): string {
  if (typeof crypto !== "undefined" && "randomUUID" in crypto) {
    return crypto.randomUUID();
  }
  return `w-${Date.now()}-${Math.random().toString(16).slice(2)}`;
}

export function emptyLayout(): DashboardLayoutPayload {
  return { version: 1, widgets: [] };
}

export function normalizeLayout(raw: unknown): DashboardLayoutPayload {
  if (!raw || typeof raw !== "object") {
    return emptyLayout();
  }
  const o = raw as Record<string, unknown>;
  const widgetsRaw = o.widgets;
  if (!Array.isArray(widgetsRaw)) {
    return { version: typeof o.version === "number" ? o.version : 1, widgets: [] };
  }
  const widgets: DashboardWidget[] = [];
  for (const item of widgetsRaw) {
    if (!item || typeof item !== "object") continue;
    const w = item as Record<string, unknown>;
    const id = typeof w.id === "string" && w.id ? w.id : newId();
    const pinned = Boolean(w.pinned);
    const type = w.type;
    if (type === "note" && typeof w.title === "string" && typeof w.body === "string") {
      widgets.push({ id, type: "note", title: w.title, body: w.body, pinned });
    } else if (
      type === "link" &&
      typeof w.title === "string" &&
      typeof w.url === "string" &&
      w.url
    ) {
      widgets.push({ id, type: "link", title: w.title, url: w.url, pinned });
    }
  }
  return { version: typeof o.version === "number" ? o.version : 1, widgets };
}

export function sortedWidgets(widgets: DashboardWidget[]): DashboardWidget[] {
  return [...widgets].sort((a, b) => {
    const ap = a.pinned ? 1 : 0;
    const bp = b.pinned ? 1 : 0;
    if (ap !== bp) return bp - ap;
    return 0;
  });
}

export { newId };
