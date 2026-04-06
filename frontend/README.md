### 开发态

前端用 pnpm run dev 跑在 5173

后端只提供 /api/* 和 /ws/*

浏览器访问 5173

### 生产态

前端先 pnpm run build

FastAPI 直接托管 frontend/dist

浏览器访问后端端口，比如 8000