/** Абсолютный URL из DRF pagination → путь для axios с baseURL `/api/v1`. */
export function toRelativeApiPath(absoluteOrRelative: string): string {
  if (!absoluteOrRelative.startsWith("http")) {
    return absoluteOrRelative.startsWith("/") ? absoluteOrRelative : `/${absoluteOrRelative}`;
  }
  try {
    const u = new globalThis.URL(absoluteOrRelative);
    const marker = "/api/v1";
    const i = u.pathname.indexOf(marker);
    if (i >= 0) {
      return `${u.pathname.slice(i + marker.length)}${u.search}`;
    }
    return `${u.pathname}${u.search}`;
  } catch {
    return absoluteOrRelative;
  }
}
