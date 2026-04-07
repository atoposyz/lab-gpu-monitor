import { apiFetch } from "./client";

export function fetchAnnouncements() {
  return apiFetch("/api/announcements");
}

export function createAnnouncement(payload) {
  return apiFetch("/api/admin/announcements", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function updateAnnouncement(id, payload) {
  return apiFetch(`/api/admin/announcements/${id}`, {
    method: "PUT",
    body: JSON.stringify(payload),
  });
}

export function disableAnnouncement(id) {
  return apiFetch(`/api/admin/announcements/${id}/disable`, {
    method: "POST",
  });
}
