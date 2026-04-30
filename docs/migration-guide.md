# 迁移指南：将现有工程迁移到 AIES 脚手架

> 本指南以 `agent-manage-backend` 为实例，描述**如何在 1-2 天内**将已有工程完整迁移到 AIES。
> 对于全新工程，直接用 `bootstrap.py` 初始化即可（见 README）。

---

## 一、迁移前准备

### 盘点现有 AI 资产

在开始前，列出工程中现有的 AI 相关文件：

```bash
cd /path/to/your-project

# 常见位置
ls -la .ai/ .aies/ .trellis/ .claude/ .cursor/ .codebuddy/ 2>/dev/null
ls -la *.md | grep -iE 'claude|agent|rule|cursor|codex'
```

### 评估成熟度

对照 `docs/philosophy.md` 的三层能力模型，你的项目处在哪个 Stage：

- **Stage 0**：什么都没有 → 直接从 `bootstrap.py --fresh` 开始
- **Stage 1**：只有 Rule / CLAUDE.md → 跳到「场景 A：轻量迁移」
- **Stage 2**：有 Rule + 索引 + 模板 → 跳到「场景 B：标准迁移」
- **Stage 3-4**：有完整 Trellis + Hooks + Multi-Agent → 跳到「场景 C：深度迁移」

---

## 二、迁移场景

### 场景 A：轻量迁移（Stage 1 → Stage 2）

**适用**：只有少量规则文件，想要正规化。

```bash
# 1. 运行 bootstrap（添加模式，不覆盖现有文件）
python3 /path/to/ai-engineering-scaffold/bootstrap.py --mode=add

# 2. 将现有 Rule.md 内容拆分进 .aies/spec/
# 手动操作，参考《规范拆分建议》章节

# 3. 精简入口文件
# 保留 CLAUDE.md、AGENTS.md，改为引用 .aies/spec/
```

### 场景 B：标准迁移（Stage 2 → Stage 2 完整版）

**适用**：已有 .ai/ 但没有会话管理。

```bash
python3 /path/to/ai-engineering-scaffold/bootstrap.py --mode=merge \
    --developer=$(whoami) \
    --language=go \
    --platforms=claude,cursor,codebuddy

# 执行后：
# - 保留你现有 .ai/ 内容
# - 新增 .aies/ 目录（workflow + tasks + workspace）
# - 生成平台入口文件（CLAUDE.md 等）
```

### 场景 C：深度迁移（已有多 Agent 体系式）

**适用**：从 Trellis / 多 Agent 体系迁移，统一目录布局。

分 6 步走：

#### Step 1：规范合并

```bash
# 目标结构
.aies/
├── spec/                    ← 所有规范集中到这里
│   ├── index.md            ← 导航
│   ├── architecture.md     ← 架构约束（从 Rule.md 二章 + trellis/spec/backend/directory-structure.md 合并）
│   ├── code-style.md       ← 代码风格
│   ├── quality-gates.md    ← 质量门
│   ├── error-handling.md
│   └── logging.md
```

操作：
```bash
# 1.1 创建目标目录
mkdir -p .aies/spec

# 1.2 按领域迁移 trellis spec
mv .trellis/spec/backend/directory-structure.md .aies/spec/architecture.md
mv .trellis/spec/backend/quality-guidelines.md .aies/spec/quality-gates.md
mv .trellis/spec/backend/error-handling.md .aies/spec/
mv .trellis/spec/backend/logging-guidelines.md .aies/spec/logging.md
mv .trellis/spec/backend/database-guidelines.md .aies/spec/

# 1.3 guides 归并
mv .trellis/spec/guides .aies/spec/guides

# 1.4 删掉 trellis spec
rm -rf .trellis/spec
```

#### Step 2：任务与日志迁移

```bash
# 直接重命名
mv .trellis/tasks .aies/tasks
mv .trellis/workspace .aies/workspace 2>/dev/null || mkdir -p .aies/workspace
mv .trellis/workflow.md .aies/workflow.md
mv .trellis/config.yaml .aies/config.yaml
```

#### Step 3：脚本整合

```bash
# 将 .trellis/scripts/ 迁移到 .aies/scripts/
mv .trellis/scripts .aies/scripts

# 更新脚本中硬编码的路径（.trellis → .aies）
find .aies/scripts -name "*.py" -exec sed -i '' 's|\.trellis|.aies|g' {} \;

# 更新 workflow.md 中的路径引用
sed -i '' 's|\.trellis|.aies|g' .aies/workflow.md
```

#### Step 4：多 Agent 配置调整

```bash
# Claude Code subagents 保留在 .claude/，但修正 context 注入路径
find .claude -name "*.py" -exec sed -i '' 's|\.trellis|.aies|g' {} \;
find .claude -name "*.md" -exec sed -i '' 's|\.trellis|.aies|g' {} \;

# 如果你不再需要多 Agent（参考 multi-agent-decision.md）
# rm -rf .claude/agents .claude/hooks
```

#### Step 5：入口文件精简

重写 `CLAUDE.md`（删除重复内容）：

```markdown
# {Project Name} — AI 规范入口

所有规范统一存放在 `.aies/spec/` 和 `.ai/`。

## 必读文件（按顺序）
1. `.aies/spec/index.md` — 规范导航
2. `.ai/index.md` — 项目地图
3. `.ai/review-checklist.md` — 代码审查清单
4. `.aies/workflow.md` — 开发工作流

## 每次会话
1. 读取上述必读文件（Claude Code 会通过 session-start Hook 自动注入）
2. 按 Phase 1 → Phase 2 → Phase 3 协议执行任务

## 平台特定规则
- 多 Agent 流水线：通过 `.claude/agents/` 启用，详见 `.aies/workflow.md`
```

类似地精简 `AGENTS.md`、`.cursorrules`、`.codebuddy/rules/`。

#### Step 6：删除冗余

```bash
# 删除 .trellis 目录（已迁移到 .aies）
rm -rf .trellis

# 检查根目录的 Rule.md 是否还需要（内容应该已迁移到 spec）
# 如果是，改为项目介绍即可
```

---

## 三、规范拆分建议

### 原 Rule.md / CLAUDE.md 的内容应该拆到哪里

| 原内容 | 目标位置 |
|--------|---------|
| 项目概述、技术栈 | `.aies/spec/architecture.md` 头部 |
| 四层架构约束 | `.aies/spec/architecture.md` |
| 命名规范、代码风格 | `.aies/spec/code-style.md` |
| 错误处理规范 | `.aies/spec/error-handling.md` |
| 日志规范 | `.aies/spec/logging.md` |
| 禁止模式 / 必须模式 | `.aies/spec/quality-gates.md` |
| 质量自检清单（8 维度） | `.ai/review-checklist.md` |
| 上下文参考指南 | `.ai/context-guide.md` |
| 业务术语表 | `.ai/glossary.md`（新增） |
| 已知技术债 | `.ai/known-issues.md`（新增） |
| Phase 1/2/3 强制执行协议 | `.aies/workflow.md` |
| Swagger 防污染规则 | `.aies/spec/code-style.md` 或单独 `.aies/spec/swagger.md` |
| 枚举注释规范 | `.aies/spec/code-style.md` |

### 拆分原则

- **方法论 & 跨项目通用** → `.aies/spec/`
- **项目实例信息** → `.ai/`
- **任务和日志** → `.aies/tasks/`、`.aies/workspace/`
- **平台适配** → `.claude/`、`.cursor/`、`.codebuddy/`（仅作引用）

---

## 四、迁移后的验证清单

执行完迁移后，过一遍：

```bash
# 1. 目录结构检查
tree -L 2 -a -I '.git|node_modules|vendor' | head -50

# 期望看到：
# .ai/
# .aies/
#   ├── spec/
#   ├── tasks/
#   ├── workspace/
#   ├── scripts/
#   ├── workflow.md
#   └── config.yaml
# .claude/ (可选)
# .cursor/ (可选)
# .codebuddy/ (可选)
# CLAUDE.md, AGENTS.md

# 2. 脚本可执行
python3 .aies/scripts/session.py get-context

# 3. AI 能正确加载
# 让 AI 执行：读取 .aies/spec/index.md 并总结项目架构
# 检查回答是否准确

# 4. 各平台入口文件不重复
diff <(cat CLAUDE.md) <(cat AGENTS.md)
# 应该是相似但不完全相同（各自引用 .aies/spec/）

# 5. 会话日志能追加
python3 .aies/scripts/session.py add --title "Migration to AIES" --summary "..."
```

---

## 五、常见问题

### Q1：迁移期间如何不影响日常开发？

建议：
- 先在 feature 分支做迁移
- AI 对话中可以同时引用新旧路径（`.aies/` 和 `.trellis/`）
- 完成后发 PR 批量切换

### Q2：多平台入口文件如何保持同步？

方案一（推荐）：入口文件都只做引用，不放实质内容
```markdown
# CLAUDE.md
See `.aies/spec/index.md` for all specifications.
```

方案二：用脚本从 `.aies/spec/` 生成各平台的入口文件
```bash
python3 .aies/scripts/sync-platforms.py
```

### Q3：老的 Trellis 日志（journal）要不要迁移？

**要**。这是项目的记忆资产：
```bash
# 原路径：.trellis/workspace/{name}/journal-N.md
# 新路径：.aies/workspace/{name}/journal-N.md
mv .trellis/workspace .aies/workspace
```

### Q4：团队成员的 `.developer` 文件怎么办？

`.aies/.developer` 是每个开发者本地的身份文件，**不应提交到 git**：

```bash
# 确认 .gitignore 中有
echo ".aies/.developer" >> .gitignore
```

### Q5：迁移后发现 Spec 有冲突（原文件同一规则写法不同）怎么办？

原则：
1. 新的 / 更严格的规则胜出
2. 保留更有例子的版本
3. 合并冲突的描述到 `.aies/spec/` 中对应章节
4. 在 `.ai/changelog.md` 记录迁移决策

---

## 六、迁移时间估算

| 项目规模 | 预计耗时 |
|---------|---------|
| 小型（<10 个 Spec 文件） | 2-4 小时 |
| 中型（约 40+ 个 Spec/源文件） | 1-2 天 |
| 大型（多个子模块，monorepo） | 3-5 天 |

---

## 七、一句话建议

> **迁移的目标不是「完美复刻」，而是「统一结构 + 消除重复 + 为未来扩展留空间」。**
> **迁移过程中**每发现一条隐性约定就立即写进 spec**，这是把隐知识显性化的最佳时机。**
