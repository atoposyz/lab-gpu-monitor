<script setup>
import { onMounted, ref } from "vue";
import { fetchAdminApplications, approveApplication, rejectApplication } from "../api/applications";

const applications = ref([]);
const selectedStatus = ref("pending");
const selectedApplication = ref(null);
const reviewComment = ref("");
const error = ref("");
const success = ref("");
const loading = ref(false);

async function loadApplications() {
  loading.value = true;
  error.value = "";
  try {
    applications.value = await fetchAdminApplications(selectedStatus.value);
    if (applications.value.length) {
      selectedApplication.value = applications.value[0];
    }
  } catch (err) {
    error.value = err.message || "加载申请失败";
  } finally {
    loading.value = false;
  }
}

function pickApplication(application) {
  selectedApplication.value = application;
  reviewComment.value = application.review_comment || "";
  success.value = "";
  error.value = "";
}

async function approve() {
  if (!selectedApplication.value) return;
  try {
    const updated = await approveApplication(selectedApplication.value.id, reviewComment.value || "批准通过");
    success.value = "申请已批准";
    selectedApplication.value = updated;
    await loadApplications();
  } catch (err) {
    error.value = err.message || "批准失败";
  }
}

async function rejectIt() {
  if (!selectedApplication.value) return;
  try {
    const updated = await rejectApplication(selectedApplication.value.id, reviewComment.value || "已驳回");
    success.value = "申请已驳回";
    selectedApplication.value = updated;
    await loadApplications();
  } catch (err) {
    error.value = err.message || "驳回失败";
  }
}

onMounted(() => {
  loadApplications();
});
</script>

<template>
  <div class="page">
    <h1 class="page-title">管理员申请审核</h1>
    <div class="toolbar">
      <div class="toolbar-group">
        <span class="toolbar-title">状态筛选：</span>
        <button class="nav-btn" :class="{ active: selectedStatus === 'pending' }" @click="selectedStatus = 'pending'; loadApplications()">待审核</button>
        <button class="nav-btn" :class="{ active: selectedStatus === 'approved' }" @click="selectedStatus = 'approved'; loadApplications()">已批准</button>
        <button class="nav-btn" :class="{ active: selectedStatus === 'rejected' }" @click="selectedStatus = 'rejected'; loadApplications()">已驳回</button>
      </div>
    </div>

    <div v-if="error" class="status-error">{{ error }}</div>
    <div v-if="success" class="status-ok">{{ success }}</div>

    <div class="admin-grid">
      <div class="card list-card">
        <h2>申请列表</h2>
        <div v-if="!applications.length" class="empty">当前没有申请</div>
        <div v-else>
          <ul class="application-list">
            <li
              v-for="item in applications"
              :key="item.id"
              :class="{ selected: selectedApplication && selectedApplication.id === item.id }"
              @click="pickApplication(item)"
            >
              <div><strong>{{ item.applicant_name }}</strong> / {{ item.email }}</div>
              <div class="small-muted">#{{ item.id }} · {{ item.status }} · {{ item.created_at }}</div>
            </li>
          </ul>
        </div>
      </div>

      <div class="card detail-card" v-if="selectedApplication">
        <h2>申请详情</h2>
        <div class="detail-row"><strong>姓名：</strong> {{ selectedApplication.applicant_name }}</div>
        <div class="detail-row"><strong>邮箱：</strong> {{ selectedApplication.email }}</div>
        <div class="detail-row"><strong>学号/工号：</strong> {{ selectedApplication.student_id || '-' }}</div>
        <div class="detail-row"><strong>导师：</strong> {{ selectedApplication.supervisor || '-' }}</div>
        <div class="detail-row"><strong>课题组：</strong> {{ selectedApplication.lab || '-' }}</div>
        <div class="detail-row"><strong>期望用户名：</strong> {{ selectedApplication.requested_username || '-' }}</div>
        <div class="detail-row"><strong>是否需要 GPU：</strong> {{ selectedApplication.need_gpu ? '是' : '否' }}</div>
        <div class="detail-row"><strong>用途：</strong> {{ selectedApplication.purpose || '-' }}</div>
        <div class="detail-row"><strong>当前状态：</strong> {{ selectedApplication.status }}</div>
        <div class="detail-row full-width">
          <label>审核备注</label>
          <textarea v-model="reviewComment" rows="4"></textarea>
        </div>
        <div class="form-actions">
          <button class="nav-btn" @click="approve">批准</button>
          <button class="nav-btn" @click="rejectIt">驳回</button>
        </div>
      </div>
    </div>
  </div>
</template>
