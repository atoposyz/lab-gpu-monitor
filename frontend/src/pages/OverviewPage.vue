<script setup>
import { computed, onMounted, ref } from "vue";
import { RouterLink } from "vue-router";
import SummaryCards from "../components/SummaryCards.vue";
import ToolbarPanel from "../components/ToolbarPanel.vue";
import UserTable from "../components/UserTable.vue";
import NodeList from "../components/NodeList.vue";
import { useOverview } from "../composables/useOverview";
import { fetchAnnouncements } from "../api/announcements";
import { useAuth } from "../composables/useAuth";
import { useQueryState } from "../composables/useQueryState";

const { data, loading, error, wsStatus } = useOverview();
const { filter, sort, gpuView } = useQueryState();
const { user, isAuthenticated, isAdmin } = useAuth();
const announcements = ref([]);
const announcementsError = ref("");

const summary = computed(() => data.value?.summary || {});
const users = computed(() => data.value?.users || []);
const nodes = computed(() => data.value?.nodes || []);
const historyUsers = computed(() => data.value?.history?.users || {});
const historyGpus = computed(() => data.value?.history?.gpus || {});
const meta = computed(() => data.value?._meta || {});

async function loadAnnouncements() {
  announcementsError.value = "";
  try {
    announcements.value = await fetchAnnouncements();
  } catch (err) {
    announcementsError.value = err.message || String(err);
  }
}

onMounted(async () => {
  await loadAnnouncements();
});
</script>

<template>
  <div class="page">
    <div class="hero-row">
      <div>
        <h1 class="page-title">实验室计算资源门户</h1>
        <p class="muted">汇聚当前 NVIDIA GPU、Slurm 作业与基础资源申请入口。</p>
      </div>
      <div class="portal-actions">
        <RouterLink class="nav-btn" to="/apply">申请计算账号</RouterLink>
        <RouterLink class="nav-btn" to="/announcements">公告</RouterLink>
        <RouterLink v-if="isAdmin" class="nav-btn" to="/admin/applications">管理员审核</RouterLink>
      </div>
    </div>

    <div class="topbar">
      <div>
        <div class="muted">
          当前用户：{{ user?.full_name || "访客" }}
          <span v-if="user">（{{ user.role }}）</span>
        </div>
      </div>
      <div class="muted">WebSocket: {{ wsStatus }}</div>
    </div>

    <div v-if="loading && !data" class="empty">加载中...</div>

    <template v-else>
      <div class="section portal-summary">
        <div class="card card-announce">
          <h2>公告</h2>
          <div v-if="announcementsError" class="muted status-error">公告加载失败: {{ announcementsError }}</div>
          <div v-if="!announcements.length" class="muted">当前没有有效公告。</div>
          <div v-else class="announcement-list">
            <div v-for="item in announcements" :key="item.id" class="announcement-item">
              <div class="announcement-header">
                <strong>{{ item.title }}</strong>
                <span class="badge" :class="`badge-${item.level}`">{{ item.level }}</span>
              </div>
              <div class="announcement-content">{{ item.content }}</div>
            </div>
          </div>
        </div>
      </div>

      <SummaryCards :summary="summary" />

      <ToolbarPanel
        :filter="filter"
        :sort="sort"
        :gpu-view="gpuView"
        @update:filter="filter = $event"
        @update:sort="sort = $event"
        @update:gpu-view="gpuView = $event"
      />

      <div class="section">
        <h2>当前用户占卡排行</h2>
        <UserTable :users="users" :history-users="historyUsers" />
      </div>

      <div class="section">
        <h2>节点视图</h2>
        <NodeList
          :nodes="nodes"
          :gpu-history="historyGpus"
          :filter="filter"
          :sort="sort"
          :gpu-view="gpuView"
        />
      </div>
    </template>
  </div>
</template>
