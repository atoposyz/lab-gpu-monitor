import { onBeforeUnmount, onMounted, ref } from "vue";
import { fetchOverview, createOverviewWebSocket } from "../api/overview";

export function useOverview() {
  const data = ref(null);
  const loading = ref(true);
  const error = ref("");
  const wsStatus = ref("connecting");

  let ws = null;
  let reconnectTimer = null;
  let pollTimer = null;
  let isUnmounted = false;

  async function loadInitial({ silent = false } = {}) {
    if (!silent) {
      loading.value = true;
    }
    error.value = "";
    try {
      data.value = await fetchOverview();
    } catch (err) {
      error.value = err?.message || String(err);
    } finally {
      if (!silent) {
        loading.value = false;
      }
    }
  }

  function stopPolling() {
    if (pollTimer) {
      clearInterval(pollTimer);
      pollTimer = null;
    }
  }

  function startPolling() {
    if (pollTimer) return;
    pollTimer = setInterval(() => {
      loadInitial({ silent: true });
    }, 5000);
  }

  function cleanupSocket() {
    if (ws) {
      ws.onopen = null;
      ws.onmessage = null;
      ws.onclose = null;
      ws.onerror = null;
      if (ws.readyState === WebSocket.OPEN || ws.readyState === WebSocket.CONNECTING) {
        ws.close();
      }
      ws = null;
    }
  }

  function connectWs() {
    if (isUnmounted) return;

    if (reconnectTimer) {
      clearTimeout(reconnectTimer);
      reconnectTimer = null;
    }

    cleanupSocket();
    wsStatus.value = "connecting";

    ws = createOverviewWebSocket({
      onOpen() {
        wsStatus.value = "connected";
        stopPolling();
      },
      onMessage(message) {
        data.value = message;
        error.value = "";
      },
      onClose() {
        if (isUnmounted) return;
        wsStatus.value = "disconnected, retrying...";
        startPolling();
        reconnectTimer = setTimeout(() => {
          connectWs();
        }, 2000);
      },
      onError(err) {
        console.error("WebSocket error:", err);
        wsStatus.value = "error, polling fallback";
        startPolling();
      },
    });
  }

  onMounted(async () => {
    await loadInitial();
    connectWs();
  });

  onBeforeUnmount(() => {
    isUnmounted = true;
    if (reconnectTimer) clearTimeout(reconnectTimer);
    stopPolling();
    cleanupSocket();
  });

  return {
    data,
    loading,
    error,
    wsStatus,
    reload: loadInitial,
  };
}
