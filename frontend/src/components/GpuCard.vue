<script setup>
import { computed } from "vue";
import {
  formatPercent,
  formatMemory,
  lastN,
  sparklinePercent,
  sparklineMemory,
} from "../utils/format";

const props = defineProps({
  nodeName: {
    type: String,
    required: true,
  },
  gpu: {
    type: Object,
    required: true,
  },
  gpuHistory: {
    type: Object,
    default: () => ({}),
  },
});

const historyKey = computed(() => `${props.nodeName}::${props.gpu.index}`);

const utilHist = computed(() => {
  const hist = props.gpuHistory[historyKey.value] || [];
  return lastN(hist.map((x) => x.util), 32);
});

const memHist = computed(() => {
  const hist = props.gpuHistory[historyKey.value] || [];
  return lastN(hist.map((x) => x.mem), 32);
});

const procCount = computed(() => {
  return props.gpu.process_count ?? (props.gpu.processes || []).length;
});

const statusInfo = computed(() => {
  const recentHighUtil = utilHist.value.some((v) => (Number(v) || 0) >= 30);

  if (props.gpu.idle_suspected) {
    return {
      text: "疑似空跑",
      badgeClass: "badge-warn",
      cardClass: "warn",
    };
  }

  if (props.gpu.is_occupied) {
    return {
      text: "正在使用",
      badgeClass: "badge-busy",
      cardClass: "busy",
    };
  }

  if (recentHighUtil) {
    return {
      text: "有活动波动",
      badgeClass: "badge-warn",
      cardClass: "idle",
    };
  }

  return {
    text: "空闲",
    badgeClass: "badge-idle",
    cardClass: "idle",
  };
});
</script>

<template>
  <div class="gpu" :class="statusInfo.cardClass">
    <div class="gpu-title-row">
      <div class="gpu-title">GPU {{ gpu.index }} - {{ gpu.name }}</div>
      <div class="right-muted">UUID: {{ gpu.uuid || "-" }}</div>
    </div>

    <div class="kv-line">
      <span class="badge" :class="statusInfo.badgeClass">{{ statusInfo.text }}</span>
      利用率: {{ formatPercent(gpu.utilization_gpu) }} |
      显存: {{ formatMemory(gpu.memory_used_mb, gpu.memory_total_mb) }} |
      温度: {{ gpu.temperature_gpu ?? "-" }}°C
    </div>

    <div class="kv-line">
      进程数: {{ procCount }}
      <template v-if="gpu.occupied_duration_human">
        | 已占用: {{ gpu.occupied_duration_human }}
      </template>
      <template v-if="gpu.idle_suspected">
        | Idle时长: {{ gpu.idle_duration_human || "" }}
      </template>
    </div>

    <div class="kv-line">
      Util历史:
      <span class="trend">{{ sparklinePercent(utilHist) }}</span>
    </div>

    <div class="kv-line">
      显存历史:
      <span class="trend">{{ sparklineMemory(memHist, gpu.memory_total_mb) }}</span>
    </div>

    <div v-if="(gpu.processes || []).length" class="proc-grid">
      <div v-for="proc in gpu.processes" :key="`${proc.pid}-${proc.user}`" class="proc">
        <div><b>用户:</b> {{ proc.user || "unknown" }}</div>
        <div><b>PID:</b> {{ proc.pid ?? "-" }}</div>
        <div><b>显存:</b> {{ proc.used_gpu_memory_mb ?? "-" }} MB</div>
        <div><b>运行时间:</b> {{ proc.runtime_human || "未知" }}</div>
        <div class="mono"><b>命令:</b> {{ proc.cmdline || proc.process_name || "-" }}</div>
      </div>
    </div>

    <div v-else class="kv-line muted">无 GPU 进程</div>
  </div>
</template>