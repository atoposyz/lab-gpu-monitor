<script setup>
import { computed } from "vue";
import { lastN, sparkline } from "../utils/format";

const props = defineProps({
  users: {
    type: Array,
    default: () => [],
  },
  historyUsers: {
    type: Object,
    default: () => ({}),
  },
});

const rows = computed(() => {
  return props.users.map((item) => {
    const hist = lastN((props.historyUsers[item.user] || []).map((x) => x.gpu_count), 24);
    return {
      ...item,
      trend: sparkline(hist),
    };
  });
});
</script>

<template>
  <div v-if="!rows.length" class="empty">当前没有检测到 GPU 进程</div>

  <table v-else>
    <thead>
      <tr>
        <th>用户</th>
        <th>占用 GPU 数</th>
        <th>进程数</th>
        <th>趋势</th>
      </tr>
    </thead>
    <tbody>
      <tr v-for="row in rows" :key="row.user">
        <td>{{ row.user }}</td>
        <td>{{ row.gpu_count ?? 0 }}</td>
        <td>{{ row.process_count ?? 0 }}</td>
        <td class="trend">{{ row.trend }}</td>
      </tr>
    </tbody>
  </table>
</template>