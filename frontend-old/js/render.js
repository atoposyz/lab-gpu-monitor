import { state } from "./state.js";
import { getQuery, setQuery } from "./query.js";
import {
  escapeHtml,
  navButton,
  formatPercent,
  formatMemory,
  naturalCompare,
  lastN,
  sparkline,
  sparklinePercent,
  sparklineMemory,
} from "./utils.js";

function setQueryAndRender(name, value) {
  setQuery(name, value);
  renderAll();
}

function bindToolbarEvents() {
  const toolbar = document.getElementById("toolbar");
  if (!toolbar) return;

  toolbar.querySelectorAll("[data-action]").forEach((btn) => {
    btn.addEventListener("click", () => {
      const action = btn.dataset.action || "";
      const match = action.match(/^setQuery\('([^']+)','([^']+)'\)$/);
      if (!match) return;
      const [, name, value] = match;
      setQueryAndRender(name, value);
    });
  });
}

export function renderToolbar() {
  const filter = getQuery("filter", "all");
  const sort = getQuery("sort", "usage");
  const gpuView = getQuery("gpu_view", "all");

  const html = `
    <div class="toolbar-group">
      <span class="toolbar-title">节点显示：</span>
      ${navButton("只显示忙碌节点", filter === "busy", "setQuery('filter','busy')")}
      ${navButton("显示全部节点", filter === "all", "setQuery('filter','all')")}
    </div>
    <div class="toolbar-group">
      <span class="toolbar-title">节点排序：</span>
      ${navButton("按使用情况排序", sort === "usage", "setQuery('sort','usage')")}
      ${navButton("按名称排序", sort === "name", "setQuery('sort','name')")}
    </div>
    <div class="toolbar-group">
      <span class="toolbar-title">GPU 显示：</span>
      ${navButton("显示所有 GPU", gpuView === "all", "setQuery('gpu_view','all')")}
      ${navButton("只显示有进程的 GPU", gpuView === "proc", "setQuery('gpu_view','proc')")}
      ${navButton("只显示疑似空跑 GPU", gpuView === "idlewarn", "setQuery('gpu_view','idlewarn')")}
    </div>
  `;

  const el = document.getElementById("toolbar");
  el.innerHTML = html;
  bindToolbarEvents();
}

export function renderSummary(data) {
  const s = data.summary || {};
  document.getElementById("summary").innerHTML = `
    <div class="card"><b>总节点数</b><br>${s.total_nodes ?? 0}</div>
    <div class="card"><b>在线节点</b><br>${s.online_nodes ?? 0}</div>
    <div class="card"><b>离线节点</b><br>${s.offline_nodes ?? 0}</div>
    <div class="card"><b>GPU 总数</b><br>${s.total_gpus ?? 0}</div>
    <div class="card"><b>忙碌 GPU</b><br>${s.busy_gpus ?? 0}</div>
    <div class="card"><b>空闲 GPU</b><br>${s.idle_gpus ?? 0}</div>
    <div class="card"><b>Slurm 作业数</b><br>${s.running_jobs ?? 0}</div>
  `;

  const m = data._meta || {};
  const statusClass = m.status === "ok" ? "status-ok" : "status-error";

  document.getElementById("meta").innerHTML =
    `缓存状态: <span class="${statusClass}">${escapeHtml(m.status ?? "-")}</span> | ` +
    `上次刷新: ${escapeHtml(m.last_update_iso ?? "-")} | ` +
    `刷新周期: ${escapeHtml(m.refresh_interval_sec ?? "-")} 秒 | ` +
    `上次采集耗时: ${escapeHtml(m.last_duration_sec ?? "-")} 秒 | ` +
    `错误: ${escapeHtml(m.last_error ?? "无")}`;
}

export function renderUsers(data) {
  const users = data.users || [];
  const userHistory = (data.history && data.history.users) || {};

  if (!users.length) {
    document.getElementById("users").innerHTML =
      `<div class="empty">当前没有检测到 GPU 进程</div>`;
    return;
  }

  let html = `
    <table>
      <thead>
        <tr>
          <th>用户</th>
          <th>占用 GPU 数</th>
          <th>进程数</th>
          <th>趋势</th>
        </tr>
      </thead>
      <tbody>
  `;

  for (const item of users) {
    const hist = lastN((userHistory[item.user] || []).map((x) => x.gpu_count), 24);
    html += `
      <tr>
        <td>${escapeHtml(item.user)}</td>
        <td>${item.gpu_count ?? 0}</td>
        <td>${item.process_count ?? 0}</td>
        <td class="trend">${sparkline(hist)}</td>
      </tr>
    `;
  }

  html += `</tbody></table>`;
  document.getElementById("users").innerHTML = html;
}

function filterAndSortNodes(data) {
  const filter = getQuery("filter", "all");
  const sort = getQuery("sort", "usage");

  let nodes = [...(data.nodes || [])];

  if (filter === "busy") {
    nodes = nodes.filter((node) => (node.busy_gpu_count > 0) || !node.reachable);
  }

  if (sort === "name") {
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

  return nodes;
}

function gpuStatusInfo(gpu, utilHist) {
  const recentHighUtil = (utilHist || []).some((v) => (Number(v) || 0) >= 30);

  if (gpu.idle_suspected) {
    return {
      text: "疑似空跑",
      badgeClass: "badge-warn",
      cardClass: "warn",
    };
  }

  if (gpu.is_occupied) {
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
}

function renderSlurmJobs(node) {
  const jobs = node.slurm_jobs || [];
  if (!jobs.length) return "";

  let html = `<div class="slurm-jobs"><b>Slurm 作业</b>`;
  for (const job of jobs) {
    html += `
      <div class="job-item">
        <div><b>JobID:</b> ${escapeHtml(job.job_id ?? "-")} | <b>用户:</b> ${escapeHtml(job.user ?? "-")} | <b>状态:</b> ${escapeHtml(job.state ?? "-")}</div>
        <div><b>名称:</b> ${escapeHtml(job.name ?? "-")}</div>
        <div><b>节点:</b> ${escapeHtml(job.nodelist ?? "-")}</div>
      </div>
    `;
  }
  html += `</div>`;
  return html;
}

function renderGpuCard(node, gpu, gpuHistory) {
  const key = `${node.name}::${gpu.index}`;
  const hist = gpuHistory[key] || [];
  const utilHist = lastN(hist.map((x) => x.util), 32);
  const memHist = lastN(hist.map((x) => x.mem), 32);

  const status = gpuStatusInfo(gpu, utilHist);
  const procCount = gpu.process_count ?? ((gpu.processes || []).length);

  let html = `
    <div class="gpu ${status.cardClass}">
      <div class="gpu-title-row">
        <div class="gpu-title">GPU ${escapeHtml(gpu.index)} - ${escapeHtml(gpu.name)}</div>
        <div class="right-muted">UUID: ${escapeHtml(gpu.uuid || "-")}</div>
      </div>

      <div class="kv-line">
        <span class="badge ${status.badgeClass}">${status.text}</span>
        利用率: ${formatPercent(gpu.utilization_gpu)} |
        显存: ${formatMemory(gpu.memory_used_mb, gpu.memory_total_mb)} |
        温度: ${escapeHtml(gpu.temperature_gpu ?? "-")}°C
      </div>

      <div class="kv-line">
        进程数: ${procCount}
        ${gpu.occupied_duration_human ? ` | 已占用: ${escapeHtml(gpu.occupied_duration_human)}` : ""}
        ${gpu.idle_suspected ? ` | Idle时长: ${escapeHtml(gpu.idle_duration_human || "")}` : ""}
      </div>

      <div class="kv-line">
        Util历史: <span class="trend">${sparklinePercent(utilHist)}</span>
      </div>

      <div class="kv-line">
        显存历史: <span class="trend">${sparklineMemory(memHist, gpu.memory_total_mb)}</span>
      </div>
  `;

  if ((gpu.processes || []).length) {
    html += `<div class="proc-grid">`;
    for (const proc of gpu.processes) {
      html += `
        <div class="proc">
          <div><b>用户:</b> ${escapeHtml(proc.user || "unknown")}</div>
          <div><b>PID:</b> ${escapeHtml(proc.pid ?? "-")}</div>
          <div><b>显存:</b> ${escapeHtml(proc.used_gpu_memory_mb ?? "-")} MB</div>
          <div><b>运行时间:</b> ${escapeHtml(proc.runtime_human || "未知")}</div>
          <div class="mono"><b>命令:</b> ${escapeHtml(proc.cmdline || proc.process_name || "-")}</div>
        </div>
      `;
    }
    html += `</div>`;
  } else {
    html += `<div class="kv-line muted">无 GPU 进程</div>`;
  }

  html += `</div>`;
  return html;
}

export function renderNodes(data) {
  const nodes = filterAndSortNodes(data);
  const gpuHistory = (data.history && data.history.gpus) || {};
  const gpuView = getQuery("gpu_view", "all");

  if (!nodes.length) {
    document.getElementById("nodes").innerHTML = `<div class="empty">暂无节点数据</div>`;
    return;
  }

  let html = "";

  for (const node of nodes) {
    let gpusToShow = [...(node.gpus || [])];

    if (gpuView === "proc") {
      gpusToShow = gpusToShow.filter(
        (gpu) => (gpu.process_count ?? ((gpu.processes || []).length)) > 0
      );
    } else if (gpuView === "idlewarn") {
      gpusToShow = gpusToShow.filter((gpu) => gpu.idle_suspected);
    }

    if (gpuView !== "all" && gpusToShow.length === 0 && node.reachable) {
      continue;
    }

    const nodeClass = node.reachable ? "node" : "node down";
    const runtime = node.runtime || {};
    const cpuUsage = runtime.cpu_usage_percent ?? "-";
    const memUsed = runtime.mem_used_mb ?? "-";
    const memTotal = runtime.mem_total_mb ?? "-";

    html += `
      <div class="${nodeClass}">
        <div class="node-header">
          <div>
            <div class="node-title">${escapeHtml(node.name)}</div>
            <div class="node-meta">
              状态: ${escapeHtml(node.state ?? "-")} |
              GRES: ${escapeHtml(node.gres ?? "-")} |
              Busy GPU: ${escapeHtml(node.busy_gpu_count ?? 0)} |
              Idle GPU: ${escapeHtml(node.idle_gpu_count ?? 0)}
            </div>
            <div class="node-runtime">
              CPU使用率: ${escapeHtml(cpuUsage)}% |
              内存: ${escapeHtml(memUsed)}/${escapeHtml(memTotal)} MB
            </div>
          </div>
          <div class="muted">
            ${node.reachable ? "节点可达" : "节点不可达 / down"}
          </div>
        </div>
    `;

    if (!node.reachable) {
      html += `<div class="empty">节点不可达，无法获取 GPU / 运行时信息</div>`;
    } else if (!gpusToShow.length) {
      html += `<div class="empty">当前筛选条件下没有可展示的 GPU</div>`;
    } else {
      for (const gpu of gpusToShow) {
        html += renderGpuCard(node, gpu, gpuHistory);
      }
    }

    html += renderSlurmJobs(node);
    html += `</div>`;
  }

  document.getElementById("nodes").innerHTML =
    html || `<div class="empty">当前筛选条件下没有节点可展示</div>`;
}

export function renderAll() {
  if (!state.latestData) return;
  renderToolbar();
  renderSummary(state.latestData);
  renderUsers(state.latestData);
  renderNodes(state.latestData);
}