export async function fetchOverview() {
  const resp = await fetch("/api/overview");
  if (!resp.ok) {
    throw new Error(`HTTP ${resp.status}`);
  }
  return await resp.json();
}

export function createOverviewWebSocket({ onOpen, onMessage, onClose, onError }) {
  const scheme = window.location.protocol === "https:" ? "wss" : "ws";
  const url = `${scheme}://${window.location.host}/ws/overview`;
  const ws = new WebSocket(url);

  ws.onopen = () => onOpen?.();
  ws.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data);
      onMessage?.(data);
    } catch (err) {
      onError?.(err);
    }
  };
  ws.onclose = () => onClose?.();
  ws.onerror = (err) => onError?.(err);

  return ws;
}