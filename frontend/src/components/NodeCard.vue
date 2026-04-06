<script setup>
import { computed } from "vue";
import GpuCard from "./GpuCard.vue";

const props = defineProps({
  node: {
    type: Object,
    required: true,
  },
  gpuHistory: {
    type: Object,
    default: () => ({}),
  },
  gpuView: {
    type: String,
    default: "all",
  },
});

const visibleGpus = computed(() => {
  let gpus = [...(props.node.gpus || [])];

  if (props.gpuView === "proc") {
    gpus = gpus.filter((gpu) => (gpu.process_count ?? (gpu.processes || []).length) > 0);
  } else if (props.gpuView === "idlewarn") {
    gpus = gpus.filter((gpu) => gpu.idle_suspected);
  }

  return gpus;
});

const runtime = computed(() => props.node.runtime || {});
</script>

<template>
  <div class="node" :class="{ down: !node.reachable }">
    <div class="node-header">
      <div>
        <div class="node-title">{{ node.name }}</div>
        <div class="node-meta">
          状态: {{ node.state ?? "-" }} |
          GRES: {{ node.gres ?? "-" }} |
          Busy GPU: {{ node.busy_gpu_count ?? 0 }} |
          Idle GPU: {{ node.idle_gpu_count ?? 0 }}
        </div>
        <div class="node-runtime">
          CPU使用率: {{ runtime.cpu_usage_percent ?? "-" }}% |
          内存: {{ runtime.mem_used_mb ?? "-" }}/{{ runtime.mem_total_mb ?? "-" }} MB
        </div>
      </div>
      <div class="muted">
        {{ node.reachable ? "节点可达" : "节点不可达 / down" }}
      </div>
    </div>

    <div v-if="!node.reachable" class="empty">
      节点不可达，无法获取 GPU / 运行时信息
    </div>

    <div v-else-if="!visibleGpus.length" class="empty">
      当前筛选条件下没有可展示的 GPU
    </div>

    <GpuCard
      v-for="gpu in visibleGpus"
      v-else
      :key="`${node.name}-${gpu.index}`"
      :node-name="node.name"
      :gpu="gpu"
      :gpu-history="gpuHistory"
    />
  </div>
</template>