import axios from "axios";
import { useAuthStore } from "@/stores/auth";

const baseURL = (import.meta.env.VITE_API_URL || "/api/v1").replace(/\/$/, "");

/** POST /media/ (multipart). Отдельный запрос без JSON Content-Type по умолчанию. */
export async function uploadMediaFile(file: File): Promise<{ id: number; url: string }> {
  const fd = new FormData();
  fd.append("file", file);
  const auth = useAuthStore();
  const headers: Record<string, string> = {};
  if (auth.accessToken) {
    headers.Authorization = `Bearer ${auth.accessToken}`;
  }
  const { data } = await axios.post<{ id: number; url: string }>(`${baseURL}/media/`, fd, { headers });
  return data;
}
