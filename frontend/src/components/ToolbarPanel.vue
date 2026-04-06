<script setup>
defineProps({
  filter: String,
  sort: String,
  gpuView: String,
});

const emit = defineEmits(["update:filter", "update:sort", "update:gpuView"]);
</script>

<template>
  <div class="toolbar">
    <div class="toolbar-group">
      <span class="toolbar-title">节点显示：</span>
      <button class="nav-btn" :class="{ active: filter === 'busy' }" @click="emit('update:filter', 'busy')">
        只显示忙碌节点
      </button>
      <button class="nav-btn" :class="{ active: filter === 'all' }" @click="emit('update:filter', 'all')">
        显示全部节点
      </button>
    </div>

    <div class="toolbar-group">
      <span class="toolbar-title">节点排序：</span>
      <button class="nav-btn" :class="{ active: sort === 'usage' }" @click="emit('update:sort', 'usage')">
        按使用情况排序
      </button>
      <button class="nav-btn" :class="{ active: sort === 'name' }" @click="emit('update:sort', 'name')">
        按名称排序
      </button>
    </div>

    <div class="toolbar-group">
      <span class="toolbar-title">GPU 显示：</span>
      <button class="nav-btn" :class="{ active: gpuView === 'all' }" @click="emit('update:gpuView', 'all')">
        显示所有 GPU
      </button>
      <button class="nav-btn" :class="{ active: gpuView === 'proc' }" @click="emit('update:gpuView', 'proc')">
        只显示有进程的 GPU
      </button>
      <button class="nav-btn" :class="{ active: gpuView === 'idlewarn' }" @click="emit('update:gpuView', 'idlewarn')">
        只显示疑似空跑 GPU
      </button>
    </div>
  </div>
</template>