import { onUnmounted, ref, shallowRef } from "vue";
import { useAuthStore } from "@/stores/auth";
import type { ChatMessage } from "@/types/messaging";

function wsUrlWithToken(accessToken: string): string {
  const explicit = (import.meta.env.VITE_WS_URL || "").trim();
  if (explicit) {
    const base = explicit.replace(/\/$/, "");
    return `${base}/ws/messaging/?token=${encodeURIComponent(accessToken)}`;
  }
  const proto = window.location.protocol === "https:" ? "wss:" : "ws:";
  const host = window.location.host;
  return `${proto}//${host}/ws/messaging/?token=${encodeURIComponent(accessToken)}`;
}

/**
 * WebSocket к `/ws/messaging/?token=` (JWT access). После connect — JSON `{ type: "subscribe", conversation: id }`.
 */
export function useMessagingSocket() {
  const connected = ref(false);
  const lastError = ref<string | null>(null);
  const wsRef = shallowRef<WebSocket | null>(null);
  let onMessageCb: ((msg: ChatMessage) => void) | null = null;

  function disconnect() {
    const s = wsRef.value;
    if (s && s.readyState === WebSocket.OPEN) {
      s.close();
    }
    wsRef.value = null;
    connected.value = false;
  }

  function connect(onMessage: (msg: ChatMessage) => void) {
    disconnect();
    onMessageCb = onMessage;
    const auth = useAuthStore();
    const token = auth.accessToken;
    if (!token) {
      lastError.value = "not_authenticated";
      return;
    }
    lastError.value = null;
    const ws = new WebSocket(wsUrlWithToken(token));
    wsRef.value = ws;
    ws.onopen = () => {
      connected.value = true;
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
        if (data.detail === "subscribed") {
          lastError.value = null;
          return;
        }
        if (
          typeof data.id === "number" &&
          typeof data.sender_id === "number" &&
          typeof data.body === "string" &&
          typeof data.created_at === "string"
        ) {
          onMessageCb?.(data as unknown as ChatMessage);
        }
      } catch {
        /* ignore malformed */
      }
    };
  }

  function subscribe(conversationId: number) {
    const ws = wsRef.value;
    if (!ws || ws.readyState !== WebSocket.OPEN) return;
    ws.send(JSON.stringify({ type: "subscribe", conversation: conversationId }));
  }

  onUnmounted(() => {
    disconnect();
    onMessageCb = null;
  });

  return {
    connected,
    lastError,
    connect,
    disconnect,
    subscribe,
  };
}
