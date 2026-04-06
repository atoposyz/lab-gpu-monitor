export function escapeHtml(str) {
  return String(str ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;");
}

export function navButton(label, active, action) {
  return `<button class="nav-btn ${active ? "active" : ""}" data-action="${escapeHtml(action)}">${label}</button>`;
}

export function formatPercent(v) {
  const n = Number(v);
  return Number.isFinite(n) ? `${n}%` : "-";
}

export function formatMemory(used, total) {
  const u = Number(used);
  const t = Number(total);
  if (!Number.isFinite(u) || !Number.isFinite(t)) return "-";
  return `${u}/${t} MB`;
}

export function naturalCompare(a, b) {
  return String(a ?? "").localeCompare(String(b ?? ""), undefined, {
    numeric: true,
    sensitivity: "base",
  });
}

export function lastN(arr, n) {
  if (!Array.isArray(arr)) return [];
  return arr.slice(Math.max(0, arr.length - n));
}

export function sparkline(values) {
  const chars = "▁▂▃▄▅▆▇█";
  if (!values || values.length === 0) return "";
  const nums = values.map((v) => Number(v) || 0);
  const maxv = Math.max(...nums, 1);
  return nums
    .map((v) => {
      const ratio = Math.max(0, Math.min(1, v / maxv));
      const idx = Math.min(chars.length - 1, Math.floor(ratio * (chars.length - 1)));
      return chars[idx];
    })
    .join("");
}

export function sparklinePercent(values) {
  const chars = "▁▂▃▄▅▆▇█";
  if (!values || values.length === 0) return "";
  return values
    .map((v) => {
      const clipped = Math.max(0, Math.min(100, Number(v) || 0));
      const idx = Math.min(chars.length - 1, Math.floor((clipped / 100) * (chars.length - 1)));
      return chars[idx];
    })
    .join("");
}

export function sparklineMemory(values, memTotal) {
  const chars = "▁▂▃▄▅▆▇█";
  if (!values || values.length === 0 || !memTotal) return "";
  return values
    .map((v) => {
      const ratio = Math.max(0, Math.min(1, (Number(v) || 0) / memTotal));
      const idx = Math.min(chars.length - 1, Math.floor(ratio * (chars.length - 1)));
      return chars[idx];
    })
    .join("");
}