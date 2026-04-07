<script setup>
import { computed } from "vue";
import { useAuth } from "./composables/useAuth";
import { RouterLink, RouterView } from "vue-router";

const { user, isAuthenticated, isAdmin, logout } = useAuth();
const currentUserLabel = computed(() => user.value ? `${user.value.full_name} (${user.value.role})` : "未登录");
</script>

<template>
  <div class="app-shell">
    <div class="app-shell-bg"></div>
    <div class="page app-shell-inner">
      <header class="app-header">
        <div class="brand-panel">
          <RouterLink class="brand brand-link" to="/">实验室计算资源门户</RouterLink>
          <p class="brand-subtitle">统一查看 GPU 资源、公告通知与账号申请进度。</p>
        </div>

        <div class="header-actions">
          <nav class="main-nav">
            <RouterLink class="nav-link" to="/">首页</RouterLink>
            <RouterLink class="nav-link" to="/announcements">公告</RouterLink>
            <RouterLink class="nav-link" to="/apply">申请账号</RouterLink>
            <RouterLink v-if="isAdmin" class="nav-link" to="/admin/applications">管理员</RouterLink>
          </nav>

          <div class="user-panel">
            <div class="user-chip">
              <span class="user-chip-label">当前身份</span>
              <strong>{{ currentUserLabel }}</strong>
            </div>
            <button v-if="isAuthenticated" class="nav-btn nav-btn-primary" @click="logout">退出</button>
            <RouterLink v-else class="nav-btn nav-btn-primary" to="/login">登录</RouterLink>
          </div>
        </div>
      </header>

      <main class="main-content">
        <RouterView />
      </main>
    </div>
  </div>
</template>
