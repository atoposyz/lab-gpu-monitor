<script setup>
import { computed, onMounted, ref } from "vue";
import { fetchAnnouncements, createAnnouncement, updateAnnouncement, disableAnnouncement } from "../api/announcements";
import { useAuth } from "../composables/useAuth";

const { isAdmin } = useAuth();
const announcements = ref([]);
const loading = ref(false);
const error = ref("");
const success = ref("");

const form = ref({
  title: "",
  content: "",
  level: "info",
  is_active: true,
  start_at: "",
  end_at: "",
});
const editId = ref(null);
const keyword = ref("");
const levelFilter = ref("all");

function createEmptyForm() {
  return {
    title: "",
    content: "",
    level: "info",
    is_active: true,
    start_at: "",
    end_at: "",
  };
}

const filteredAnnouncements = computed(() => {
  const normalizedKeyword = keyword.value.trim().toLowerCase();

  return announcements.value.filter((item) => {
    const matchLevel = levelFilter.value === "all" || item.level === levelFilter.value;
    const matchKeyword = !normalizedKeyword
      || item.title?.toLowerCase().includes(normalizedKeyword)
      || item.content?.toLowerCase().includes(normalizedKeyword);
    return matchLevel && matchKeyword;
  });
});

const stats = computed(() => ({
  total: announcements.value.length,
  active: announcements.value.filter((item) => item.is_active).length,
  warning: announcements.value.filter((item) => item.level === "warning" || item.level === "critical").length,
}));

function formatDateTime(value) {
  if (!value) return "未设置";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;
  return new Intl.DateTimeFormat("zh-CN", {
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
  }).format(date);
}

function resetForm() {
  form.value = createEmptyForm();
  editId.value = null;
}

async function loadAnnouncements() {
  loading.value = true;
  error.value = "";
  try {
    announcements.value = await fetchAnnouncements();
  } catch (err) {
    error.value = err.message || "公告加载失败";
  } finally {
    loading.value = false;
  }
}

async function submitAnnouncement() {
  error.value = "";
  success.value = "";
  try {
    if (editId.value) {
      await updateAnnouncement(editId.value, form.value);
      success.value = "公告已更新";
    } else {
      await createAnnouncement(form.value);
      success.value = "公告已创建";
    }
    resetForm();
    await loadAnnouncements();
  } catch (err) {
    error.value = err.message || "保存公告失败";
  }
}

function startEdit(item) {
  editId.value = item.id;
  form.value = {
    title: item.title,
    content: item.content,
    level: item.level,
    is_active: item.is_active,
    start_at: item.start_at || "",
    end_at: item.end_at || "",
  };
  success.value = "";
  error.value = "";
}

function cancelEdit() {
  resetForm();
  success.value = "";
  error.value = "";
}

async function disableItem(item) {
  try {
    await disableAnnouncement(item.id);
    success.value = "公告已停用";
    await loadAnnouncements();
  } catch (err) {
    error.value = err.message || "停用失败";
  }
}

onMounted(() => {
  loadAnnouncements();
});
</script>

<template>
  <div class="page">
    <div class="hero-row">
      <div>
        <h1 class="page-title">公告中心</h1>
        <p class="muted">统一查看系统通知、维护提醒和资源使用公告。</p>
      </div>
      <div v-if="isAdmin" class="portal-actions">
        <a class="nav-btn" href="#announcement-form">{{ editId ? "继续编辑" : "发布公告" }}</a>
      </div>
    </div>

    <div class="summary">
      <div class="card stat-card">
        <span class="stat-label">公告总数</span>
        <strong class="stat-value">{{ stats.total }}</strong>
      </div>
      <div class="card stat-card">
        <span class="stat-label">当前启用</span>
        <strong class="stat-value">{{ stats.active }}</strong>
      </div>
      <div class="card stat-card">
        <span class="stat-label">重点提醒</span>
        <strong class="stat-value">{{ stats.warning }}</strong>
      </div>
    </div>

    <div v-if="error" class="status-banner status-banner-error">{{ error }}</div>
    <div v-if="success" class="status-banner status-banner-ok">{{ success }}</div>

    <div class="toolbar">
      <div class="toolbar-group toolbar-group-wide">
        <span class="toolbar-title">搜索公告</span>
        <input v-model="keyword" type="text" placeholder="按标题或内容检索" />
      </div>
      <div class="toolbar-group">
        <span class="toolbar-title">级别筛选</span>
        <select v-model="levelFilter">
          <option value="all">全部</option>
          <option value="info">信息</option>
          <option value="warning">提醒</option>
          <option value="critical">紧急</option>
        </select>
      </div>
    </div>

    <div class="section">
      <div class="section-heading">
        <h2>公告列表</h2>
        <span class="small-muted">共 {{ filteredAnnouncements.length }} 条结果</span>
      </div>
      <div v-if="loading" class="empty">公告加载中...</div>
      <div v-else-if="!filteredAnnouncements.length" class="empty">当前筛选条件下暂无公告</div>
      <div v-else class="announcement-list">
        <div
          v-for="item in filteredAnnouncements"
          :key="item.id"
          class="announcement-item announcement-card"
          :class="{ inactive: !item.is_active }"
        >
          <div class="announcement-header">
            <div class="announcement-title-group">
              <strong>{{ item.title }}</strong>
              <span class="small-muted">创建于 {{ formatDateTime(item.created_at) }}</span>
            </div>
            <div class="announcement-tags">
              <span class="badge" :class="`badge-${item.level}`">{{ item.level }}</span>
              <span class="badge" :class="item.is_active ? 'badge-active' : 'badge-inactive'">
                {{ item.is_active ? "启用中" : "已停用" }}
              </span>
            </div>
          </div>
          <div class="announcement-content">{{ item.content }}</div>
          <div class="announcement-meta-grid">
            <div class="small-muted">开始时间：{{ formatDateTime(item.start_at) }}</div>
            <div class="small-muted">结束时间：{{ formatDateTime(item.end_at) }}</div>
          </div>
          <div v-if="isAdmin" class="form-actions">
            <button class="nav-btn" @click="startEdit(item)">编辑</button>
            <button class="nav-btn" :disabled="!item.is_active" @click="disableItem(item)">停用</button>
          </div>
        </div>
      </div>
    </div>

    <div v-if="isAdmin" id="announcement-form" class="section card form-card">
      <h2>{{ editId ? '编辑公告' : '创建公告' }}</h2>
      <p class="muted form-intro">发布后会立即在门户首页和公告中心展示，适合用于停机维护、重要提醒和一般通知。</p>
      <div class="form-grid">
        <div class="form-group full-width">
          <label>标题</label>
          <input v-model="form.title" type="text" placeholder="例如：周末机房维护通知" />
        </div>
        <div class="form-group full-width">
          <label>内容</label>
          <textarea v-model="form.content" rows="5" placeholder="填写公告正文、影响范围和建议操作"></textarea>
        </div>
        <div class="form-group">
          <label>级别</label>
          <select v-model="form.level">
            <option value="info">info</option>
            <option value="warning">warning</option>
            <option value="critical">critical</option>
          </select>
        </div>
        <div class="form-group">
          <label>启用</label>
          <select v-model="form.is_active">
            <option :value="true">是</option>
            <option :value="false">否</option>
          </select>
        </div>
        <div class="form-group">
          <label>开始时间</label>
          <input v-model="form.start_at" type="datetime-local" />
        </div>
        <div class="form-group">
          <label>结束时间</label>
          <input v-model="form.end_at" type="datetime-local" />
        </div>
      </div>
      <div class="form-actions">
        <button class="nav-btn nav-btn-primary" @click="submitAnnouncement">{{ editId ? '保存更新' : '创建公告' }}</button>
        <button v-if="editId" class="nav-btn" @click="cancelEdit">取消编辑</button>
      </div>
    </div>
  </div>
</template>
