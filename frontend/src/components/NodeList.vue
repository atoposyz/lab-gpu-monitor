<script setup>
import { computed } from "vue";
import NodeCard from "./NodeCard.vue";
import { naturalCompare } from "../utils/format";

const props = defineProps({
  nodes: {
    type: Array,
    default: () => [],
  },
  gpuHistory: {
    type: Object,
    default: () => ({}),
  },
  filter: {
    type: String,
    default: "all",
  },
  sort: {
    type: String,
    default: "usage",
  },
  gpuView: {
    type: String,
    default: "all",
  },
});

const visibleNodes = computed(() => {
  let nodes = [...props.nodes];

  if (props.filter === "busy") {
    nodes = nodes.filter((node) => (node.busy_gpu_count > 0) || !node.reachable);
  }

  if (props.sort === "name") {
    nodes.sort((a, b) => naturalCompare(a.name, b.name));
  } else {
    nodes.sort((a, b) => {
      const aReach = a.reachable ? 0 : 1;
      const bReach = b.reachable ? 0 : 1;
      if (aReach !== bReach) return aReach - bReach;

      if ((a.busy_gpu_count || 0) !== (b.busy_gpu_count || 0)) {
        return (b.busy_gpu_count || 0) - (a.busy_gpu_count || 0);
      }

      const aUtil = (a.gpus || []).reduce((sum, g) => sum + (g.utilization_gpu || 0), 0);
      const bUtil = (b.gpus || []).reduce((sum, g) => sum + (g.utilization_gpu || 0), 0);
      if (aUtil !== bUtil) return bUtil - aUtil;

      return naturalCompare(a.name, b.name);
    });
  }

  if (props.gpuView === "all") {
    return nodes;
  }

  return nodes.filter((node) => {
    if (!node.reachable) return true;
    const gpus = node.gpus || [];
    if (props.gpuView === "proc") {
      return gpus.some((gpu) => (gpu.process_count ?? (gpu.processes || []).length) > 0);
    }
    if (props.gpuView === "idlewarn") {
      return gpus.some((gpu) => gpu.idle_suspected);
    }
    return true;
  });
});
</script>

<template>
  <div v-if="!visibleNodes.length" class="empty">
    当前筛选条件下没有节点可展示
  </div>

  <NodeCard
    v-for="node in visibleNodes"
    v-else
    :key="node.name"
    :node="node"
    :gpu-history="gpuHistory"
    :gpu-view="gpuView"
  />
</template>