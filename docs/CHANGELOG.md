# Changelog

## 2026-03-21

### 新增
- **后端 API 服务**：FastAPI + SQLAlchemy + SQLite
  - 用户认证：注册/登录/JWT 鉴权
  - 积分系统：注册赠送 100 积分，对话扣费，余额查询，交易历史
  - 课程管理：创建课程，查看课程列表，获取对话历史
  - AI 对话：接入 DashScope API (glm-5)，SSE 流式响应
  - 健康检查端点
- **前端 Web 应用**：React 19 + Vite + Tailwind CSS
  - 登录/注册页面
  - 课程仪表板（课程列表 + 新建课程）
  - 对话页面（实时流式 Markdown 渲染）
  - 积分明细页面
  - JWT 认证状态管理（AuthContext）
  - 路由保护（ProtectedRoute / GuestRoute）
- **Docker 容器化**：backend Dockerfile + frontend Dockerfile + docker-compose.yml
- **测试套件**：16 个 pytest 单元测试覆盖 auth、credits、courses、health

### 修复
- 修复 auth.py 中 `pwd_context` 未定义导致注册/登录全部失败的 bug
- 修复 `/api/health` 端点被 static files mount 拦截返回 404 的问题
- 修正测试中无认证请求状态码断言（401 vs 403 兼容）
