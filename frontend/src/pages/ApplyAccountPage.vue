<script setup>
import { onMounted, ref } from "vue";
import { createApplication, fetchMyApplications } from "../api/applications";

const form = ref({
  applicant_name: "",
  email: "",
  student_id: "",
  supervisor: "",
  lab: "",
  requested_username: "",
  ssh_public_key: "",
  need_gpu: true,
  purpose: "",
});
const submitting = ref(false);
const error = ref("");
const success = ref("");
const applications = ref([]);

async function loadApplications() {
  try {
    applications.value = await fetchMyApplications();
  } catch (err) {
    error.value = err.message || "加载申请记录失败";
  }
}

async function submitForm() {
  error.value = "";
  success.value = "";
  submitting.value = true;
  try {
    await createApplication(form.value);
    success.value = "申请已提交，已保存到我的申请记录。";
    form.value = {
      applicant_name: "",
      email: "",
      student_id: "",
      supervisor: "",
      lab: "",
      requested_username: "",
      ssh_public_key: "",
      need_gpu: true,
      purpose: "",
    };
    await loadApplications();
  } catch (err) {
    error.value = err.message || "提交申请失败";
  } finally {
    submitting.value = false;
  }
}

onMounted(() => {
  loadApplications();
});
</script>

<template>
  <div class="page">
    <h1 class="page-title">计算资源账号申请</h1>

    <div class="card form-card">
      <div class="form-grid">
        <div class="form-group">
          <label>姓名</label>
          <input v-model="form.applicant_name" type="text" />
        </div>
        <div class="form-group">
          <label>邮箱</label>
          <input v-model="form.email" type="email" />
        </div>
        <div class="form-group">
          <label>学号/工号</label>
          <input v-model="form.student_id" type="text" />
        </div>
        <div class="form-group">
          <label>导师</label>
          <input v-model="form.supervisor" type="text" />
        </div>
        <div class="form-group">
          <label>课题组</label>
          <input v-model="form.lab" type="text" />
        </div>
        <div class="form-group">
          <label>期望用户名</label>
          <input v-model="form.requested_username" type="text" />
        </div>
        <div class="form-group full-width">
          <label>SSH 公钥</label>
          <textarea v-model="form.ssh_public_key" rows="3"></textarea>
        </div>
        <div class="form-group full-width">
          <label>是否需要 GPU</label>
          <select v-model="form.need_gpu">
            <option :value="true">是</option>
            <option :value="false">否</option>
          </select>
        </div>
        <div class="form-group full-width">
          <label>用途说明</label>
          <textarea v-model="form.purpose" rows="4"></textarea>
        </div>
      </div>

      <div class="form-actions">
        <button class="nav-btn" @click="submitForm" :disabled="submitting">提交申请</button>
      </div>
      <div v-if="error" class="status-error">{{ error }}</div>
      <div v-if="success" class="status-ok">{{ success }}</div>
    </div>

    <div class="section">
      <h2>我的申请记录</h2>
      <div v-if="!applications.length" class="empty">暂无申请记录</div>
      <div v-else class="table-card">
        <table>
          <thead>
            <tr>
              <th>ID</th>
              <th>姓名</th>
              <th>邮箱</th>
              <th>状态</th>
              <th>提交时间</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in applications" :key="item.id">
              <td>{{ item.id }}</td>
              <td>{{ item.applicant_name }}</td>
              <td>{{ item.email }}</td>
              <td>{{ item.status }}</td>
              <td>{{ item.created_at }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>
