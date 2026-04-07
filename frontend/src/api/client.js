function getToken() {
  return window.localStorage.getItem("token") || "";
}

function buildHeaders(customHeaders = {}) {
  const headers = {
    "Content-Type": "application/json",
    ...customHeaders,
  };
  const token = getToken();
  if (token) {
    headers.Authorization = `Bearer ${token}`;
  }
  return headers;
}

export async function apiFetch(path, options = {}) {
  const response = await fetch(path, {
    headers: buildHeaders(options.headers),
    ...options,
  });

  const text = await response.text();
  const data = text ? JSON.parse(text) : null;

  if (!response.ok) {
    const message = data?.detail || data?.message || response.statusText;
    throw new Error(message || `HTTP ${response.status}`);
  }

  return data;
}
