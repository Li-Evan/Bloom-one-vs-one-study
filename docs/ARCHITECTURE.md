# Bloom 学习系统 · 架构文档

## 项目概述

基于 Bloom 2-Sigma 理论的文档驱动式学习系统。通过 AI（DashScope glm-5）模拟一对一苏格拉底式导师，以结构化 Markdown 课文为载体，支持行内批注和反馈驱动的自适应学习。

## 技术栈

| 层 | 技术 | 说明 |
|---|------|------|
| 前端 | React 19 + Vite + Tailwind CSS | SPA，SSE 流式 AI 响应 |
| 后端 | FastAPI + SQLAlchemy + SQLite | REST API + SSE 流式生成 |
| AI | DashScope API (OpenAI 兼容协议) | glm-5 模型 |
| 认证 | JWT (python-jose + bcrypt) | Bearer Token |
| 容器 | Docker + docker-compose | 前后端分离部署 |

## 系统架构

```
┌─────────────────────┐
│   React Frontend    │
│  (Vite dev / nginx) │
│                     │
│  Pages:             │
│  - DashboardPage    │  课程列表 + 新建
│  - CoursePage       │  大纲 + 课文列表 + 总结
│  - LessonPage       │  Markdown阅读 + 批注 + 反馈
│  - CreditsPage      │  积分明细
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
│  │ Courses Router│  │  课程/大纲/课文/批注/反馈/生成/总结 (12个端点)
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
│   │   ├── models.py       # ORM 模型：User, CreditTransaction, Course, Syllabus, Lesson, Annotation, Feedback
│   │   ├── schemas.py      # Pydantic 请求/响应模型 + 输入验证
│   │   ├── auth.py         # 认证路由 + JWT + bcrypt 密码处理
│   │   ├── credits.py      # 积分路由 + 扣费/退款函数
│   │   └── courses.py      # 课程路由 + AI System Prompts + 课文生成逻辑
│   ├── tests/
│   │   ├── conftest.py     # pytest 配置，内存 SQLite，auth_client fixture
│   │   └── unit/           # 单元测试（auth, credits, courses, lessons, health）
│   ├── pyproject.toml      # 依赖声明（uv 管理）
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── main.jsx        # React 入口
│   │   ├── App.jsx         # 路由定义 + ProtectedRoute / GuestRoute
│   │   ├── lib/
│   │   │   ├── api.js      # HTTP 客户端 + SSE 流式处理（12个课程API函数）
│   │   │   └── AuthContext.jsx  # 全局认证状态
│   │   └── pages/
│   │       ├── LoginPage.jsx      # 登录
│   │       ├── RegisterPage.jsx   # 注册
│   │       ├── DashboardPage.jsx  # 课程仪表盘（卡片列表+状态）
│   │       ├── CoursePage.jsx     # 课程详情（大纲+课文列表+总结）
│   │       ├── LessonPage.jsx    # 课文阅读（Markdown+批注+反馈+AI生成）
│   │       └── CreditsPage.jsx    # 积分明细
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
- `id`, `user_id`(FK), `amount`, `balance_after`, `type`, `description`, `created_at`

### Course（课程）
- `id`, `user_id`(FK), `name`, `status`(learning/completed, CheckConstraint), `created_at`
- 关系：`syllabus`（一对一）, `lessons`（一对多，cascade delete）

### Syllabus（大纲）
- `id`, `course_id`(FK unique, ondelete CASCADE), `content`(Markdown), `created_at`

### Lesson（课文）
- `id`, `course_id`(FK, ondelete CASCADE), `number`(1,2,3... 0=总结), `content`(Markdown), `is_evaluation`(bool), `created_at`
- 关系：`annotations`（一对多，cascade delete）, `feedback`（一对一，cascade delete）

### Annotation（行内批注）
- `id`, `lesson_id`(FK, ondelete CASCADE), `user_id`(FK), `position_start`, `position_end`(CheckConstraint: end >= start), `original_text`, `comment`, `created_at`

### Feedback（反馈）
- `id`, `lesson_id`(FK, ondelete CASCADE), `user_id`(FK), `content`, `thought_answers`(JSON string), `created_at`

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

### 课程 `/api`

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/courses` | 创建课程（AI 生成大纲 + 第一篇课文） |
| GET | `/courses` | 列出当前用户的课程 |
| GET | `/courses/{id}` | 课程详情（含大纲内容） |
| GET | `/courses/{id}/syllabus` | 获取大纲 |
| PUT | `/courses/{id}/syllabus` | 更新大纲（勾选掌握项） |
| GET | `/courses/{id}/lessons` | 获取课文列表 |
| GET | `/courses/{id}/lessons/{num}` | 获取某篇课文 |
| POST | `/courses/{id}/lessons/{num}/annotations` | 保存行内批注 |
| GET | `/courses/{id}/lessons/{num}/annotations` | 获取批注 |
| POST | `/courses/{id}/lessons/{num}/feedback` | 提交反馈（支持更新） |
| POST | `/courses/{id}/next` | "我读完了" → AI 生成下一篇（SSE） |
| GET | `/courses/{id}/summary` | 获取完结总结 |
| GET | `/health` | 健康检查 |

## 核心流程

### 课程创建流程（`POST /courses`）

1. 验证认证 + 扣除积分
2. AI 生成课程大纲（非流式，阻塞调用）
3. AI 生成第一篇课文（非流式）
4. 保存 Course + Syllabus + Lesson 到 DB
5. 返回课程详情（含大纲和课文数）

### 生成下一篇（`POST /courses/{id}/next`）

1. 验证认证 + 课程归属 + 扣除积分
2. 检查最后一篇课文是否为评估篇：
   - **是评估篇** → 生成总结（SSE），标记课程为 completed
   - **不是评估篇** → 检查大纲掌握项是否全部完成：
     - **全部完成** → 生成评估篇（SSE，`<!-- eval-article -->` 标记）
     - **未全部完成** → 生成续篇（SSE，含思考题复盘 + ??? 解答 + 正文）
3. SSE 逐 chunk 返回给前端实时渲染
4. 流结束后保存 Lesson 到 DB

### AI System Prompts

- `SYLLABUS_PROMPT`: 生成课程大纲（掌握项 checkbox、不在范围内、学习进度表格）
- `FIRST_LESSON_PROMPT`: 首篇课文（标题、元信息、正文、思考题、反馈区）
- `NEXT_LESSON_PROMPT`: 续篇课文（思考题复盘 → ??? 解答 → 正文 → 思考题）
- `EVAL_LESSON_PROMPT`: 评估篇（`<!-- eval-article -->` 标记，无新内容）
- `SUMMARY_PROMPT`: 课程总结（知识图谱、大纲复盘、关键洞察、延伸方向）

### 认证流程

- 注册时 bcrypt 哈希密码，赠送 100 积分（写入 CreditTransaction）
- 登录返回 JWT（24h 有效期）
- 前端存储 token 到 localStorage，每次请求带 `Authorization: Bearer <token>`

## 前端路由

| 路由 | 页面 | 说明 |
|------|------|------|
| `/` | DashboardPage | 课程卡片列表（状态：学习中/已完成） |
| `/course/:id` | CoursePage | 左侧大纲（Markdown） + 右侧课文列表 |
| `/course/:id/lesson/:num` | LessonPage | Markdown 渲染 + 选中文本批注 + 反馈区 + "我读完了"按钮 |
| `/credits` | CreditsPage | 积分余额 + 交易记录 |
| `/login` | LoginPage | 登录 |
| `/register` | RegisterPage | 注册 |

## 配置项

通过 `.env` 文件管理（详见 `.env.example`）：

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `DASHSCOPE_API_KEY` | — | 阿里百炼 API 密钥（必填） |
| `DASHSCOPE_BASE_URL` | `https://coding.dashscope.aliyuncs.com/v1` | API 地址 |
| `DASHSCOPE_MODEL` | `glm-5` | 模型名称 |
| `JWT_SECRET_KEY` | — | JWT 密钥（必填，≥32字符） |
| `JWT_EXPIRE_MINUTES` | `1440` | Token 有效期（分钟） |
| `DEFAULT_CREDITS` | `100` | 注册赠送积分 |
| `CREDITS_PER_REQUEST` | `1` | 每次操作消耗积分 |
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
