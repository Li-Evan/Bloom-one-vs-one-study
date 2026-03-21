# Bloom 学习系统 · 架构文档

## 项目概述

基于 Bloom 2-Sigma 理论的交互式学习系统。通过 AI（DashScope glm-5）模拟一对一苏格拉底式导师，为用户提供自适应的学习体验。

## 技术栈

| 层 | 技术 | 说明 |
|---|------|------|
| 前端 | React 19 + Vite + Tailwind CSS | SPA，SSE 流式对话 |
| 后端 | FastAPI + SQLAlchemy + SQLite | REST API + 流式响应 |
| AI | DashScope API (OpenAI 兼容协议) | glm-5 模型 |
| 认证 | JWT (python-jose + bcrypt) | Bearer Token |
| 容器 | Docker + docker-compose | 前后端分离部署 |

## 系统架构

```
┌─────────────────────┐
│   React Frontend    │
│  (Vite dev / nginx) │
└─────────┬───────────┘
          │ HTTP / SSE
          ▼
┌─────────────────────┐
│   FastAPI Backend   │
│                     │
│  ┌───────────────┐  │
│  │ Auth Router   │  │  POST /api/auth/register, /login, GET /me
│  ├───────────────┤  │
│  │ Credits Router│  │  GET /api/credits/balance, /history
│  ├───────────────┤  │
│  │ Chat Router   │  │  POST /api/courses, GET /courses, POST /chat/send (SSE)
│  └───────────────┘  │
│          │          │
│  ┌───────────────┐  │
│  │  SQLAlchemy   │  │
│  │   (SQLite)    │  │
│  └───────────────┘  │
└─────────┬───────────┘
          │ HTTPS (OpenAI SDK)
          ▼
┌─────────────────────┐
│  DashScope API      │
│  (glm-5 模型)       │
└─────────────────────┘
```

## 目录结构

```
Bloom-one-vs-one-study/
├── backend/
│   ├── app/
│   │   ├── main.py         # FastAPI 应用入口，路由注册，CORS，静态文件
│   │   ├── config.py       # 环境变量配置（Settings dataclass）
│   │   ├── database.py     # SQLAlchemy 引擎 + Session 工厂
│   │   ├── models.py       # ORM 模型：User, CreditTransaction, Course, Message
│   │   ├── schemas.py      # Pydantic 请求/响应模型
│   │   ├── auth.py         # 认证路由 + JWT + bcrypt 密码处理
│   │   ├── credits.py      # 积分路由 + 扣费函数
│   │   └── chat.py         # 课程管理 + DashScope 流式对话
│   ├── tests/
│   │   ├── conftest.py     # pytest 配置，测试数据库，auth_client fixture
│   │   └── unit/           # 单元测试（auth, credits, courses, health）
│   ├── pyproject.toml      # 依赖声明（uv 管理）
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── main.jsx        # React 入口
│   │   ├── App.jsx         # 路由定义 + ProtectedRoute / GuestRoute
│   │   ├── lib/
│   │   │   ├── api.js      # HTTP 客户端 + SSE 流式处理
│   │   │   └── AuthContext.jsx  # 全局认证状态
│   │   └── pages/          # LoginPage, RegisterPage, DashboardPage, ChatPage, CreditsPage
│   ├── package.json
│   └── Dockerfile
├── docker-compose.yml
├── .env.example
└── docs/
    ├── ARCHITECTURE.md     # 本文件
    └── CHANGELOG.md
```

## 数据模型

### User（用户）
- `id`, `email`, `username`, `password_hash`, `credits`（默认 100）, `created_at`

### CreditTransaction（交易记录）
- `id`, `user_id`(FK), `amount`, `balance_after`, `type`(registration_bonus/chat_deduction/admin_topup), `description`, `created_at`

### Course（课程）
- `id`, `user_id`(FK), `name`, `created_at`
- 关系：`messages`（按时间排序的对话历史）

### Message（消息）
- `id`, `course_id`(FK), `role`(user/assistant/system), `content`, `tokens_used`, `created_at`

## API 端点

### 认证 `/api/auth`

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/register` | 注册，赠送初始积分 |
| POST | `/login` | 登录，返回 JWT |
| GET | `/me` | 获取当前用户信息 |

### 积分 `/api/credits`

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/balance` | 查询积分余额 |
| GET | `/history` | 交易记录（最近 50 条） |

### 课程与对话 `/api`

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/courses` | 创建课程 |
| GET | `/courses` | 列出当前用户的课程 |
| GET | `/courses/{id}/messages` | 获取课程对话历史 |
| POST | `/chat/send` | 发送消息，返回 SSE 流 |
| GET | `/health` | 健康检查 |

## 核心流程

### 对话流程（`/api/chat/send`）

1. 验证用户认证 + 课程归属
2. 原子化扣除积分（SQL WHERE 条件确保余额充足，防竞态）
3. 保存用户消息到 DB
4. 构建对话历史（system prompt + 历史消息）
5. 调用 DashScope API（流式），逐 chunk 通过 SSE 返回给前端
6. 流结束后：保存 AI 回复到 DB
7. 前端通过 `onChunk` 回调实时渲染

### 认证流程

- 注册时 bcrypt 哈希密码，赠送 100 积分（写入 CreditTransaction）
- 登录返回 JWT（24h 有效期）
- 前端存储 token 到 localStorage，每次请求带 `Authorization: Bearer <token>`

## 配置项

通过 `.env` 文件管理（详见 `.env.example`）：

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `DASHSCOPE_API_KEY` | — | 阿里百炼 API 密钥（必填） |
| `DASHSCOPE_BASE_URL` | `https://coding.dashscope.aliyuncs.com/v1` | API 地址 |
| `DASHSCOPE_MODEL` | `glm-5` | 模型名称 |
| `JWT_SECRET_KEY` | `""`（空字符串） | JWT 密钥（必填，启动时校验，不安全值会拒绝启动） |
| `JWT_EXPIRE_MINUTES` | `1440` | Token 有效期（分钟） |
| `DEFAULT_CREDITS` | `100` | 注册赠送积分 |
| `CREDITS_PER_REQUEST` | `1` | 每次对话消耗积分 |
| `DATABASE_URL` | `sqlite:///./bloom.db` | 数据库连接 |

## 开发命令

```bash
# 后端
cd backend && uv run uvicorn app.main:app --reload --port 8000

# 前端
cd frontend && npm run dev

# 测试
cd backend && uv run pytest tests/ -v

# Docker
docker-compose up --build
```
