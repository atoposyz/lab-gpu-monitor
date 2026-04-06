<script setup>
defineProps({
  summary: {
    type: Object,
    default: () => ({}),
  },
});
</script>

<template>
  <div class="summary">
    <div class="card"><b>总节点数</b><br />{{ summary.total_nodes ?? 0 }}</div>
    <div class="card"><b>在线节点</b><br />{{ summary.online_nodes ?? 0 }}</div>
    <div class="card"><b>离线节点</b><br />{{ summary.offline_nodes ?? 0 }}</div>
    <div class="card"><b>GPU 总数</b><br />{{ summary.total_gpus ?? 0 }}</div>
    <div class="card"><b>忙碌 GPU</b><br />{{ summary.busy_gpus ?? 0 }}</div>
    <div class="card"><b>空闲 GPU</b><br />{{ summary.idle_gpus ?? 0 }}</div>
    <div class="card"><b>Slurm 作业数</b><br />{{ summary.running_jobs ?? 0 }}</div>
  </div>
</template>