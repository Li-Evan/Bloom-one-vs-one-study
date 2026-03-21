# Changelog

## 2026-03-21 (v2 — 文档驱动式学习系统)

### 重大改造
- **从聊天系统改造为文档驱动式学习系统**
  - 课程不再是对话历史，而是一系列结构化 Markdown 课文
  - 每篇课文包含：正文、思考题、反馈区
  - 续篇自动包含：上篇思考题复盘 → ??? 解答 → 新正文
  - 评估篇（掌握项全部完成时）+ 自动生成课程总结

### 后端新增
- **数据模型**：Course(+status)、Syllabus、Lesson、Annotation、Feedback
  - cascade delete：删课程自动清理大纲/课文/批注/反馈
  - CheckConstraint：course.status 限制为 learning/completed，annotation position_end >= position_start
- **12 个 API 端点**：
  - 课程 CRUD：创建（含 AI 生成大纲+首篇）、列表、详情
  - 大纲：获取、更新（勾选掌握项）
  - 课文：列表、详情
  - 批注：创建、获取
  - 反馈：提交（支持 upsert）
  - 生成：下一篇（SSE 流式）—— 自动判断续篇/评估篇/总结
  - 总结：获取完结总结
- **5 套 AI System Prompt**：大纲、首篇、续篇、评估篇、总结
- **输入验证**：position_end >= position_start (schema)、thought_answers JSON 格式校验
- **积分扣费集成**：创建课程和生成课文都扣费，失败自动退款

### 前端改造
- **DashboardPage**：课程卡片显示状态（学习中/已完成）和课文数
- **CoursePage**（新增）：左侧大纲（Markdown 渲染，带 checkbox）+ 右侧课文列表 + 总结展示
- **LessonPage**（新增，替代 ChatPage）：
  - Markdown 课文渲染
  - 选中文本添加行内批注（弹窗交互）
  - 反馈表单（文本 + 思考题 JSON 回答）
  - "我读完了"按钮 → AI 流式生成下一篇
- **api.js**：新增 12 个课程相关 API 函数
- **路由更新**：`/course/:id` 和 `/course/:id/lesson/:num`
- 删除旧 ChatPage.jsx

### 测试
- **43 个 pytest 测试全部通过**
  - 保留原有 auth(9) + credits(8) + health(1) 测试
  - 新增 courses 测试(11)：创建、列表、详情、大纲、课文、积分不足
  - 新增 lessons 测试(14)：批注 CRUD、反馈 CRUD、位置验证、JSON 验证、生成下一篇、评估篇、总结
- 前端 `npm run build` 通过

### 文档
- 更新 ARCHITECTURE.md：完整反映新数据模型、12 个 API 端点、核心流程、前端路由
- 更新 CHANGELOG.md：本文件

---

## 2026-03-21 (v1 — 初始聊天系统)

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
- 修复 config.py JWT 安全校验遗漏 `.env.example` 默认值
- 修复 chat.py 积分不足错误信息引用 stale ORM 数据的问题
- SSE 流式输出改用 `ensure_ascii=False`，正确显示中文字符
