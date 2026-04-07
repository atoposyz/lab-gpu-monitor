import { computed, ref } from "vue";
import { login as loginApi, fetchMe as fetchMeApi } from "../api/auth";

const user = ref(JSON.parse(window.localStorage.getItem("user") || "null"));
const token = ref(window.localStorage.getItem("token") || "");
const loading = ref(false);
const error = ref("");

function syncStorage() {
  if (token.value) {
    window.localStorage.setItem("token", token.value);
  } else {
    window.localStorage.removeItem("token");
  }

  if (user.value) {
    window.localStorage.setItem("user", JSON.stringify(user.value));
  } else {
    window.localStorage.removeItem("user");
  }
}

async function login(username, password) {
  loading.value = true;
  error.value = "";
  try {
    const data = await loginApi({ username, password });
    token.value = data.access_token;
    user.value = data.user;
    syncStorage();
    return data;
  } catch (err) {
    error.value = err.message || "Login failed";
    throw err;
  } finally {
    loading.value = false;
  }
}

async function fetchMe() {
  if (!token.value) {
    user.value = null;
    syncStorage();
    return null;
  }
  try {
    const data = await fetchMeApi();
    user.value = data;
    syncStorage();
    return data;
  } catch (err) {
    logout();
    throw err;
  }
}

function logout() {
  token.value = "";
  user.value = null;
  syncStorage();
}

const isAuthenticated = computed(() => Boolean(user.value));
const isAdmin = computed(() => user.value?.role === "admin");

export function useAuth() {
  return {
    user,
    token,
    loading,
    error,
    isAuthenticated,
    isAdmin,
    login,
    fetchMe,
    logout,
  };
}
