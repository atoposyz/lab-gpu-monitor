import { onBeforeUnmount, onMounted, ref } from "vue";
import { fetchOverview, createOverviewWebSocket } from "../api/overview";

export function useOverview() {
  const data = ref(null);
  const loading = ref(true);
  const error = ref("");
  const wsStatus = ref("connecting");

  let ws = null;
  let reconnectTimer = null;

  async function loadInitial() {
    loading.value = true;
    error.value = "";
    try {
      data.value = await fetchOverview();
    } catch (err) {
      error.value = err?.message || String(err);
    } finally {
      loading.value = false;
    }
  }

  function connectWs() {
    if (reconnectTimer) {
      clearTimeout(reconnectTimer);
      reconnectTimer = null;
    }

    wsStatus.value = "connecting";

    ws = createOverviewWebSocket({
      onOpen() {
        wsStatus.value = "connected";
      },
      onMessage(message) {
        data.value = message;
      },
      onClose() {
        wsStatus.value = "disconnected, retrying...";
        reconnectTimer = setTimeout(() => {
          connectWs();
        }, 2000);
      },
      onError(err) {
        console.error("WebSocket error:", err);
        wsStatus.value = "error";
      },
    });
  }

  onMounted(async () => {
    await loadInitial();
    connectWs();
  });

  onBeforeUnmount(() => {
    if (reconnectTimer) clearTimeout(reconnectTimer);
    if (ws) ws.close();
  });

  return {
    data,
    loading,
    error,
    wsStatus,
    reload: loadInitial,
  };
}