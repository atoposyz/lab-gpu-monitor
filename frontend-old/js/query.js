export function getQuery(name, fallback) {
  const url = new URL(window.location.href);
  return url.searchParams.get(name) || fallback;
}

export function setQuery(name, value) {
  const url = new URL(window.location.href);
  url.searchParams.set(name, value);
  history.replaceState({}, "", url);
}