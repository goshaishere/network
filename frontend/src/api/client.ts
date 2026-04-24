import axios from "axios";

const raw = import.meta.env.VITE_API_URL || "/api/v1";
const baseURL = raw.replace(/\/$/, "");

export const api = axios.create({
  baseURL,
  headers: { "Content-Type": "application/json" },
  withCredentials: false,
});
