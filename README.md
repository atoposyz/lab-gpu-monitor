# lab-gpu-monitor

一个面向实验室集群的 GPU 监控面板。  
后端通过 `Slurm + SSH + nvidia-smi + ps/top/free` 采集节点、GPU、进程和用户占卡信息；前端通过 `REST API + WebSocket` 展示总览、用户排行、节点卡片和 GPU 历史趋势。

当前项目包含两套前端：

- `frontend/`：当前使用中的 Vue 3 + Vite 前端，推荐使用
- `frontend-old/`：早期静态版前端，保留作参考

## 功能概览

- 汇总节点在线状态、GPU 总量、忙碌/空闲 GPU 数、Slurm 作业数
- 按用户统计 GPU 占用数和进程数
- 展示节点 CPU/内存、GPU 利用率/显存/温度/进程信息
- 记录 GPU 与用户的短期历史数据并生成趋势图
- 识别“疑似空跑 GPU”
- 通过 WebSocket 推送最新缓存结果

## 运行前提

使用本项目之前，建议先确认以下条件：

- Python `>= 3.12`
- Node.js + npm
- 已安装 `uv`
- 机器可执行 `squeue`、`sinfo`
- 当前用户可通过 SSH 免密访问 Slurm 节点
- 节点上可执行 `nvidia-smi`、`ps`、`top`、`free`

如果上面任一条件不满足，后端采集结果可能为空，或只能拿到部分信息。

## 技术架构

数据流大致如下：

1. `backend/collectors/slurm.py` 读取 Slurm 的作业和节点列表
2. `backend/collectors/ssh.py` 通过 SSH 登录目标节点
3. `backend/collectors/gpu.py`、`backend/collectors/node.py` 在节点上执行 `nvidia-smi`、`ps`、`top`、`free`
4. `backend/services/overview.py` 聚合为统一概览数据
5. `backend/services/cache.py` 周期刷新缓存、维护历史趋势和 idle 判定
6. `backend/main.py` 通过 `/api/overview` 和 `/ws/overview` 对外提供数据
7. `frontend/` 读取 API 和 WebSocket 数据并渲染页面

## 快速开始

### 1. 安装后端依赖

在项目根目录执行：

```bash
uv sync
```

### 2. 开发模式

开发模式下：

- 后端运行在 `8000`
- 前端 Vite 开发服务器运行在 `5173`
- 前端通过 Vite 代理访问 `/api` 和 `/ws`

启动：

```bash
cd /home/aistation/lab-gpu-monitor
./run_dev.sh
```

访问地址：

- 前端：`http://127.0.0.1:5173`
- 后端接口：`http://127.0.0.1:8000/api/overview`
- 健康检查：`http://127.0.0.1:8000/api/health`

停止：

```bash
./stop_dev.sh
```

### 3. 生产模式

生产模式下：

- 前端先构建到 `frontend/dist`
- 后端以 `APP_ENV=prod` 启动
- FastAPI 直接托管构建后的静态页面

启动：

```bash
cd /home/aistation/lab-gpu-monitor
./run_prod.sh
```

访问地址：

- 页面与接口统一由后端端口提供，默认 `http://127.0.0.1:8000`

停止：

```bash
./stop_prod.sh
```

## 手动运行方式

如果你不想使用脚本，也可以手动启动。

### 后端

开发模式：

```bash
cd /home/aistation/lab-gpu-monitor
APP_ENV=dev uv run uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```

生产模式：

```bash
cd /home/aistation/lab-gpu-monitor
APP_ENV=prod uv run uvicorn backend.main:app --host 0.0.0.0 --port 8000
```

### 前端

开发：

```bash
cd /home/aistation/lab-gpu-monitor/frontend
npm install
npm run dev -- --host 0.0.0.0 --port 5173
```

构建：

```bash
cd /home/aistation/lab-gpu-monitor/frontend
npm run build
```

预览构建结果：

```bash
cd /home/aistation/lab-gpu-monitor/frontend
npm run preview
```

## 常用接口

### `GET /api/health`

返回服务状态、缓存元信息和当前运行模式。

### `GET /api/overview`

返回完整监控数据，包括：

- `summary`：汇总指标
- `users`：用户占卡排行
- `nodes`：节点与 GPU 详情
- `history`：GPU 与用户历史趋势
- `_meta`：缓存刷新状态

### `WS /ws/overview`

当缓存时间戳变化时推送最新概览 JSON，默认约每 2 秒检查一次。

## 运行脚本说明

### `run_dev.sh`

- 检查 `8000`、`5173` 端口是否被占用
- 启动后端热重载服务
- 如 `frontend/node_modules` 不存在则自动执行 `npm install`
- 启动 Vite 前端开发服务器
- 记录 PID 到 `logs/`

### `stop_dev.sh`

- 根据 `logs/backend_dev.pid`、`logs/frontend_dev.pid` 停止开发服务

### `run_prod.sh`

- 如需先安装前端依赖则自动执行 `npm install`
- 执行 `npm run build`
- 启动 `APP_ENV=prod` 后端并托管 `frontend/dist`

### `stop_prod.sh`

- 根据 `logs/backend_prod.pid` 停止生产服务

## 采集测试

项目提供了一个简单的采集验证脚本：

```bash
cd /home/aistation/lab-gpu-monitor
uv run python scripts/test_collect.py
```

这个脚本会打印：

- Slurm 作业列表
- 节点列表
- GPU 节点列表
- 每个 GPU 节点的 GPU 摘要
- 每个 GPU 节点的 GPU 进程列表

适合在排查 SSH、Slurm 或 `nvidia-smi` 采集异常时使用。

## 环境变量

项目里实际用到的环境变量包括：

- `APP_ENV`：`dev` 或 `prod`
- `BACKEND_HOST`：后端监听地址，默认 `0.0.0.0`
- `BACKEND_PORT`：后端端口，默认 `8000`
- `FRONTEND_HOST`：前端开发服务器监听地址，默认 `0.0.0.0`
- `FRONTEND_PORT`：前端开发服务器端口，默认 `5173`

## 项目树与文件作用

下面的树状结构以“源码和关键文件”为主，`node_modules/`、`.venv/`、`.git/`、`dist/` 这类依赖或构建产物不展开。

```text
lab-gpu-monitor/
├── README.md
├── pyproject.toml
├── uv.lock
├── run_dev.sh
├── stop_dev.sh
├── run_prod.sh
├── stop_prod.sh
├── backend/
│   ├── __init__.py
│   ├── main.py
│   ├── collectors/
│   │   ├── __init__.py
│   │   ├── slurm.py
│   │   ├── ssh.py
│   │   ├── gpu.py
│   │   └── node.py
│   ├── models/
│   │   └── __init__.py
│   └── services/
│       ├── __init__.py
│       ├── overview.py
│       └── cache.py
├── frontend/
│   ├── README.md
│   ├── package.json
│   ├── pnpm-lock.yaml
│   ├── vite.config.js
│   ├── index.html
│   ├── public/
│   │   ├── favicon.svg
│   │   └── icons.svg
│   └── src/
│       ├── main.js
│       ├── App.vue
│       ├── style.css
│       ├── api/
│       │   └── overview.js
│       ├── composables/
│       │   ├── useOverview.js
│       │   └── useQueryState.js
│       ├── components/
│       │   ├── SummaryCards.vue
│       │   ├── ToolbarPanel.vue
│       │   ├── UserTable.vue
│       │   ├── NodeList.vue
│       │   ├── NodeCard.vue
│       │   └── GpuCard.vue
│       └── utils/
│           └── format.js
├── frontend-old/
│   ├── index.html
│   ├── styles.css
│   └── js/
│       ├── app.js
│       ├── api.js
│       ├── query.js
│       ├── render.js
│       ├── state.js
│       └── utils.js
├── scripts/
│   └── test_collect.py
└── logs/
    ├── backend_dev.log / backend_dev.pid
    ├── frontend_dev.log / frontend_dev.pid
    └── backend_prod.log / backend_prod.pid
```

### 根目录文件

- `README.md`：项目总说明文档。
- `pyproject.toml`：Python 项目配置，声明依赖 `fastapi`、`uvicorn`、`pydantic`、`websockets`。
- `uv.lock`：`uv` 生成的 Python 锁文件，用于固定依赖版本。
- `run_dev.sh`：一键启动开发环境。
- `stop_dev.sh`：停止开发环境的前后端进程。
- `run_prod.sh`：构建前端并启动生产模式服务。
- `stop_prod.sh`：停止生产模式后端服务。

### backend/

- `backend/__init__.py`：后端包标记文件。
- `backend/main.py`：FastAPI 入口；暴露 `/api/health`、`/api/overview`、`/ws/overview`；在生产模式下托管 `frontend/dist`。

### backend/collectors/

- `backend/collectors/__init__.py`：采集器包标记文件。
- `backend/collectors/slurm.py`：调用 `squeue`、`sinfo`，读取 Slurm 作业和节点基础信息。
- `backend/collectors/ssh.py`：封装 SSH 调用，配置连接复用、超时和容错逻辑。
- `backend/collectors/gpu.py`：在远端节点执行 `nvidia-smi` 与 `ps`，收集 GPU 摘要、GPU 进程、进程用户和运行时长。
- `backend/collectors/node.py`：在远端节点执行 `top` 和 `free`，获取 CPU 与内存运行态指标。

### backend/models/

- `backend/models/__init__.py`：模型包占位文件；当前还没有拆分出独立数据模型。

### backend/services/

- `backend/services/__init__.py`：服务层包标记文件。
- `backend/services/overview.py`：汇总所有采集结果，生成统一的 `summary/users/nodes` 数据结构。
- `backend/services/cache.py`：周期刷新缓存，维护 GPU/用户历史趋势、占用时长和“疑似空跑”状态。

### frontend/

- `frontend/README.md`：前端的简短运行说明。
- `frontend/package.json`：前端依赖和脚本定义，包含 `dev`、`build`、`preview`。
- `frontend/pnpm-lock.yaml`：前端锁文件；即便当前脚本使用 `npm`，也能反映依赖版本。
- `frontend/vite.config.js`：Vite 配置；开发态把 `/api`、`/ws` 代理到 `127.0.0.1:8000`。
- `frontend/index.html`：Vite 前端入口 HTML。

### frontend/public/

- `frontend/public/favicon.svg`：站点图标。
- `frontend/public/icons.svg`：页面中可复用的 SVG 图标资源。

### frontend/src/

- `frontend/src/main.js`：Vue 应用入口，挂载 `App.vue`。
- `frontend/src/App.vue`：页面主布局，组合顶部状态栏、汇总卡片、筛选面板、用户表格和节点列表。
- `frontend/src/style.css`：全局样式。

### frontend/src/api/

- `frontend/src/api/overview.js`：封装 `/api/overview` 请求和 `/ws/overview` WebSocket 连接。

### frontend/src/composables/

- `frontend/src/composables/useOverview.js`：管理初始数据加载、WebSocket 自动重连和页面数据状态。
- `frontend/src/composables/useQueryState.js`：把筛选条件同步到 URL 查询参数，便于刷新和分享当前视图。

### frontend/src/components/

- `frontend/src/components/SummaryCards.vue`：展示节点数、GPU 数、作业数等汇总指标卡片。
- `frontend/src/components/ToolbarPanel.vue`：控制节点筛选、排序方式和 GPU 展示模式。
- `frontend/src/components/UserTable.vue`：展示用户 GPU 占用排行和用户维度趋势字符图。
- `frontend/src/components/NodeList.vue`：根据筛选条件组织节点列表，并控制排序逻辑。
- `frontend/src/components/NodeCard.vue`：展示单个节点状态、运行时信息和其下属 GPU 列表。
- `frontend/src/components/GpuCard.vue`：展示单张 GPU 的状态、历史趋势、进程详情和疑似空跑提示。

### frontend/src/utils/

- `frontend/src/utils/format.js`：格式化百分比、显存、自然排序和字符趋势图工具函数。

### frontend-old/

- `frontend-old/index.html`：旧版前端主页。
- `frontend-old/styles.css`：旧版前端样式。
- `frontend-old/js/app.js`：旧版前端入口。
- `frontend-old/js/api.js`：旧版前端接口访问逻辑。
- `frontend-old/js/query.js`：旧版前端 URL 参数处理。
- `frontend-old/js/render.js`：旧版前端 DOM 渲染逻辑。
- `frontend-old/js/state.js`：旧版前端状态管理。
- `frontend-old/js/utils.js`：旧版前端工具函数。

### scripts/

- `scripts/test_collect.py`：独立测试采集链路的脚本，用于检查作业、节点、GPU 和进程采集是否正常。

### logs/

- `logs/backend_dev.log`：开发模式后端日志。
- `logs/backend_dev.pid`：开发模式后端 PID。
- `logs/frontend_dev.log`：开发模式前端日志。
- `logs/frontend_dev.pid`：开发模式前端 PID。
- `logs/backend_prod.log`：生产模式后端日志。
- `logs/backend_prod.pid`：生产模式后端 PID。

## 目录使用建议

- 日常开发优先使用 `frontend/`，`frontend-old/` 仅作历史参考。
- 如果页面数据为空，优先执行 `uv run python scripts/test_collect.py` 检查采集链路。
- 如果前端可以打开但没有数据，通常先检查后端 `logs/backend_dev.log` 或 `logs/backend_prod.log`。
- 如果 WebSocket 不更新，先确认后端缓存是否在刷新，再检查 `/ws/overview` 是否被代理或放通。

## 已知实现特点

- 节点是否“可达”目前主要基于 Slurm 节点状态是否包含 `down`
- GPU “占用”判定基于“存在进程”或“显存使用量 >= 500MB”
- GPU “疑似空跑”判定基于“有进程、低利用率、低显存，并持续一段时间”
- `backend/models/` 目前还是预留目录，暂未真正承载数据模型

