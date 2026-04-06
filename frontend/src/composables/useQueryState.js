import { ref, watch } from "vue";

function getUrl() {
  return new URL(window.location.href);
}

function readQuery(name, fallback) {
  return getUrl().searchParams.get(name) || fallback;
}

function writeQuery(name, value) {
  const url = getUrl();
  url.searchParams.set(name, value);
  history.replaceState({}, "", url);
}

export function useQueryState() {
  const filter = ref(readQuery("filter", "all"));
  const sort = ref(readQuery("sort", "usage"));
  const gpuView = ref(readQuery("gpu_view", "all"));

  watch(filter, (v) => writeQuery("filter", v));
  watch(sort, (v) => writeQuery("sort", v));
  watch(gpuView, (v) => writeQuery("gpu_view", v));

  window.addEventListener("popstate", () => {
    filter.value = readQuery("filter", "all");
    sort.value = readQuery("sort", "usage");
    gpuView.value = readQuery("gpu_view", "all");
  });

  return {
    filter,
    sort,
    gpuView,
  };
}