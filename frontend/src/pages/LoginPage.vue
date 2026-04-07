<script setup>
import { ref } from "vue";
import { useRouter } from "vue-router";
import { useAuth } from "../composables/useAuth";

const router = useRouter();
const { login, error, loading } = useAuth();
const username = ref("");
const password = ref("");
const formError = ref("");

async function submit() {
  formError.value = "";
  try {
    await login(username.value, password.value);
    router.push({ name: "Overview" });
  } catch (err) {
    formError.value = err.message || "登录失败";
  }
}
</script>

<template>
  <div class="page">
    <h1 class="page-title">登录</h1>
    <div class="form-card">
      <div class="form-group">
        <label>用户名</label>
        <input v-model="username" type="text" placeholder="admin" />
      </div>
      <div class="form-group">
        <label>密码</label>
        <input v-model="password" type="password" placeholder="密码" />
      </div>
      <div class="form-actions">
        <button class="nav-btn" @click="submit" :disabled="loading">登录</button>
      </div>
      <div v-if="formError || error" class="status-error">
        {{ formError || error }}
      </div>
    </div>
  </div>
</template>
