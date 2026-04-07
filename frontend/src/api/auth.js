import { apiFetch } from "./client";

export function login(payload) {
  return apiFetch("/api/auth/login", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function fetchMe() {
  return apiFetch("/api/auth/me");
}
