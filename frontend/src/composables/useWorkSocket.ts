import { onUnmounted, ref, shallowRef } from "vue";
import { useAuthStore } from "@/stores/auth";

function wsUrlWithToken(accessToken: string): string {
  const explicit = (import.meta.env.VITE_WS_URL || "").trim();
  if (explicit) {
    const base = explicit.replace(/\/$/, "");
    return `${base}/ws/work/?token=${encodeURIComponent(accessToken)}`;
  }
  const proto = window.location.protocol === "https:" ? "wss:" : "ws:";
  const host = window.location.host;
  return `${proto}//${host}/ws/work/?token=${encodeURIComponent(accessToken)}`;
}

export function useWorkSocket() {
  const connected = ref(false);
  const lastError = ref<string | null>(null);
  const wsRef = shallowRef<WebSocket | null>(null);
  let onEventCb: ((event: Record<string, unknown>) => void) | null = null;

  function disconnect() {
    const s = wsRef.value;
    if (s && s.readyState === WebSocket.OPEN) s.close();
    wsRef.value = null;
    connected.value = false;
  }

  function connect(onEvent: (event: Record<string, unknown>) => void) {
    disconnect();
    onEventCb = onEvent;
    const auth = useAuthStore();
    if (!auth.accessToken) {
      lastError.value = "not_authenticated";
      return;
    }
    const ws = new WebSocket(wsUrlWithToken(auth.accessToken));
    wsRef.value = ws;
    ws.onopen = () => {
      connected.value = true;
      lastError.value = null;
    };
    ws.onclose = () => {
      connected.value = false;
    };
    ws.onerror = () => {
      lastError.value = "ws_error";
    };
    ws.onmessage = (ev) => {
      try {
        const data = JSON.parse(ev.data) as Record<string, unknown>;
        if (typeof data.error === "string") {
          lastError.value = data.error;
          return;
        }
        onEventCb?.(data);
      } catch {
        // ignore malformed event
      }
    };
  }

  function subscribe(boardId: number) {
    const ws = wsRef.value;
    if (!ws || ws.readyState !== WebSocket.OPEN) return;
    ws.send(JSON.stringify({ type: "subscribe", board: boardId }));
  }

  onUnmounted(disconnect);

  return { connected, lastError, connect, disconnect, subscribe };
}
