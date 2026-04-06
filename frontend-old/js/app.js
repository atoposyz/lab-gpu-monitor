import { state } from "./state.js";
import { fetchOverview, connectOverviewWebSocket } from "./api.js";
import { renderAll } from "./render.js";
import { escapeHtml } from "./utils.js";

async function loadInitial() {
  try {
    const data = await fetchOverview();
    state.latestData = data;
    renderAll();
  } catch (err) {
    const meta = document.getElementById("meta");
    if (meta) {
      meta.innerHTML = `初始加载失败: ${escapeHtml(err?.message || String(err))}`;
    }
  }
}

function initWebSocket() {
  connectOverviewWebSocket((data) => {
    state.latestData = data;
    renderAll();
  });
}

async function bootstrap() {
  await loadInitial();
  initWebSocket();
}

bootstrap();