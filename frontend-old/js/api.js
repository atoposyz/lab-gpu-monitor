import { state } from "./state.js";

export async function fetchOverview() {
  const resp = await fetch("/api/overview");
  if (!resp.ok) {
    throw new Error(`HTTP ${resp.status}`);
  }
  return await resp.json();
}

export function updateWsStatus(text) {
  const el = document.getElementById("ws-status");
  if (el) el.textContent = text;
}

export function connectOverviewWebSocket(onData) {
  if (state.reconnectTimer) {
    clearTimeout(state.reconnectTimer);
    state.reconnectTimer = null;
  }

  const scheme = window.location.protocol === "https:" ? "wss" : "ws";
  const wsUrl = `${scheme}://${window.location.host}/ws/overview`;

  updateWsStatus("WebSocket: connecting");
  state.ws = new WebSocket(wsUrl);

  state.ws.onopen = () => {
    updateWsStatus("WebSocket: connected");
  };

  state.ws.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data);
      onData(data);
    } catch (err) {
      console.error("WS message parse error:", err);
    }
  };

  state.ws.onclose = () => {
    updateWsStatus("WebSocket: disconnected, retrying...");
    state.reconnectTimer = setTimeout(() => {
      connectOverviewWebSocket(onData);
    }, 2000);
  };

  state.ws.onerror = () => {
    updateWsStatus("WebSocket: error");
    try {
      state.ws.close();
    } catch (err) {
      console.error("WS close error:", err);
    }
  };
}