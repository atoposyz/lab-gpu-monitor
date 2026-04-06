<script setup>
import { computed } from "vue";
import SummaryCards from "./components/SummaryCards.vue";
import ToolbarPanel from "./components/ToolbarPanel.vue";
import UserTable from "./components/UserTable.vue";
import NodeList from "./components/NodeList.vue";
import { useOverview } from "./composables/useOverview";
import { useQueryState } from "./composables/useQueryState";

const { data, loading, error, wsStatus } = useOverview();
const { filter, sort, gpuView } = useQueryState();

const summary = computed(() => data.value?.summary || {});
const users = computed(() => data.value?.users || []);
const nodes = computed(() => data.value?.nodes || []);
const historyUsers = computed(() => data.value?.history?.users || {});
const historyGpus = computed(() => data.value?.history?.gpus || {});
const meta = computed(() => data.value?._meta || {});

const metaStatusClass = computed(() => {
  return meta.value.status === "ok" ? "status-ok" : "status-error";
});
</script>

<template>
  <div class="page">
    <div class="topbar">
      <div>
        <h1 class="page-title">实验室 GPU 监控面板</h1>
        <div v-if="error" class="muted status-error">初始加载失败: {{ error }}</div>
        <div v-else class="muted">
          缓存状态:
          <span :class="metaStatusClass">{{ meta.status ?? "-" }}</span>
          |
          上次刷新: {{ meta.last_update_iso ?? "-" }}
          |
          刷新周期: {{ meta.refresh_interval_sec ?? "-" }} 秒
          |
          上次采集耗时: {{ meta.last_duration_sec ?? "-" }} 秒
          |
          错误: {{ meta.last_error ?? "无" }}
        </div>
      </div>
      <div class="muted">WebSocket: {{ wsStatus }}</div>
    </div>

    <div v-if="loading && !data" class="empty">加载中...</div>

    <template v-else>
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