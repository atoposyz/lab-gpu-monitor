import { apiFetch } from "./client";

export function createApplication(payload) {
  return apiFetch("/api/applications", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function fetchMyApplications() {
  return apiFetch("/api/applications/me");
}

export function fetchAdminApplications(status) {
  const query = status ? `?status=${encodeURIComponent(status)}` : "";
  return apiFetch(`/api/admin/applications${query}`);
}

export function approveApplication(id, review_comment) {
  return apiFetch(`/api/admin/applications/${id}/approve`, {
    method: "POST",
    body: JSON.stringify({ review_comment }),
  });
}

export function rejectApplication(id, review_comment) {
  return apiFetch(`/api/admin/applications/${id}/reject`, {
    method: "POST",
    body: JSON.stringify({ review_comment }),
  });
}
