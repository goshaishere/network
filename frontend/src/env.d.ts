/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_API_URL: string;
  readonly VITE_HCAPTCHA_SITEKEY?: string;
  /** Полный базовый URL для WS (например `wss://api.example.com`), без пути `/ws/messaging`. */
  readonly VITE_WS_URL?: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}
