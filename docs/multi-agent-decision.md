# 你需要多 Agent 吗？—— 决策指南

> **先说结论：大多数项目不需要。把单 Agent + Spec 用好，已经比 90% 的团队做得好了。**

---

## 一、先定义：什么叫「多 Agent」

在 AI 开发上下文中，"多 Agent" 通常指三种形态：

### 形态 1：角色专精（Role-Specialized）

一个主 Agent 把任务分派给不同角色的子 Agent：
- `plan` —— 做需求分析和技术方案
- `implement` —— 写代码
- `check` —— 跑 lint/test、审查代码
- `debug` —— 修 Bug
- `research` —— 查文档、搜代码库

**典型实现**：Claude Code subagents、LangGraph、CrewAI、AutoGen

### 形态 2：流水线（Pipeline）

固定顺序串联多个 Agent，每步有明确输入输出：

```
研究 → 设计 → 实现 → 自检 → 调试 → 提 PR
 ↓      ↓      ↓      ↓      ↓      ↓
[research][plan][impl][check][debug][create-pr]
```

**典型实现**：Go 管理后端服务中的 dispatch 模式（详见 `docs/agent-manage-backend-review.md`）

### 形态 3：并行 + 协作（Parallel Team）

多个 Agent 同时工作、互相通信：
- 前端 Agent + 后端 Agent 并行
- 用共享的 task.json / 消息队列协作

**典型实现**：git worktree + Claude Code Team 模式

---

## 二、多 Agent 能解决什么、不能解决什么

### ✅ 能解决

| 问题 | 如何解决 |
|------|---------|
| **长耗时任务中断** | 每个子 Agent 独立超时，不会全盘失败 |
| **上下文过载** | 每个 Agent 只需加载自己相关的 Spec 子集 |
| **盲区不同** | 不同角色的 Agent 关注不同检查项 |
| **并行提速** | 多任务真正并行（worktree + 独立分支） |
| **审查独立性** | check Agent 和 implement Agent 独立判断 |

### ❌ 不能解决

| 误区 | 真相 |
|------|------|
| 认为多 Agent = 代码质量自动变高 | 没有 Spec，多 Agent 只会产出多种风格的垃圾 |
| 认为多 Agent 能替代人审查 | Agent 互评仍有共同盲区（都被同一 Prompt 塑造） |
| 认为多 Agent 能理解业务 | 只能理解 Spec 里写过的业务 |
| 认为多 Agent = 全自动 | 需要大量 orchestration 代码 + Hooks 维护 |

---

## 三、决策矩阵：你属于哪种场景

### 🟢 场景 1：单人业务开发（推荐单 Agent）

```
特征：
- 团队 1-3 人
- 业务明确，每次任务 <2 小时
- 有明确 Spec 的情况下 AI 产出能复用

推荐方案：
- 单 Agent + 完整 Spec + review-checklist + 会话日志
- 你就是 orchestrator，AI 是实习生
```

### 🟡 场景 2：小团队多任务并行（考虑轻量流水线）

```
特征：
- 团队 3-10 人
- 多人同时用 AI 开发不同功能
- 担心 AI 产出互相冲突

推荐方案：
- 单 Agent 为主
- 引入 task.json 和 worktree 隔离
- 需要并行时用「plan + implement + check」三阶段
```

### 🟠 场景 3：复杂项目有明确流程（引入多 Agent）

```
特征：
- 项目有固定的开发流程（需求 → 设计 → 编码 → 测试 → 上线）
- 某些步骤可自动化（如代码审查、测试生成）
- 团队 >10 人，规范体系成熟

推荐方案：
- 引入 dispatch/implement/check/debug 流水线
- Hooks 自动注入上下文（见 .claude/hooks/）
- CI 跑 AI Review 作为门禁
```

### 🔴 场景 4：Agent 平台 / 基础设施团队（深度多 Agent）

```
特征：
- 你在做 AI Agent 平台本身
- 需要研究不同编排模式
- 不计较 orchestration 成本

推荐方案：
- 采用 Parallel Team 模式
- 自己写 MCP Server 暴露内部工具
- 引入 LangGraph / CrewAI 等专业框架
```

---

## 四、引入多 Agent 的成本清单

很多人低估了多 Agent 的维护成本。真实账单：

| 成本项 | 具体工作 |
|--------|---------|
| **Agent 定义** | 每个 Agent 一份 Prompt（200-500 行），占 20% 精力 |
| **Context 注入** | 写 Hooks / 写 jsonl 上下文配置，占 30% 精力 |
| **任务状态管理** | task.json 设计、状态流转、失败重试 |
| **超时与重试** | 每个 Agent 独立超时策略，失败回滚设计 |
| **Agent 间通信** | 共享内存文件 / 消息队列 / task 目录 |
| **平台差异** | Claude Code 有 subagents，Cursor 没有，抽象成本 |
| **调试难度** | 一个 Bug 可能涉及 3 个 Agent，排查链路长 |

**经验法则**：如果多 Agent 节省的时间 < 维护成本，就不要上。

---

## 五、渐进采用路径（推荐）

不要一步到位，按阶段演进：

### Stage 0：纯手工 AI（无脚手架）

直接用 Copilot / ChatGPT，每次贴代码。**不可持续**。

### Stage 1：规范 + 索引（AIES 第 1 层）

- 加入 `.ai/index.md` / `.ai/review-checklist.md` / `.ai/prompts/`
- 加入 `.aies/spec/` 存架构/代码风格/错误处理规范
- 各平台入口文件引用这些文件
- **产出**：单 Agent 产出即达标，团队规范统一

### Stage 2：任务管理 + 会话日志（AIES 第 2 层）

- 加入 `.aies/tasks/` 管理任务状态
- 加入 `.aies/workspace/{developer}/journal.md` 记录每次会话
- 加入 `session.py` 和 `task.py` 辅助脚本
- **产出**：跨会话不失忆，多人协作有痕迹

### Stage 3：Slash 命令 + Hooks（AIES 第 3 层·轻）

- 加入 `/aies:start` 自动初始化会话
- 加入 `/aies:finish-work` 自动输出完成清单
- Claude Code 加入 SessionStart Hook
- **产出**：AI 行为一致性显著提高

### Stage 4：多 Agent 流水线（AIES 第 3 层·重）

- 引入 `dispatch → research → plan → implement → check → debug`
- 每个 Agent 有专属 context jsonl
- Hooks 自动注入上下文
- **产出**：复杂任务自动化完成，适合大团队

### Stage 5：CI 集成 + 质量门禁

- GitHub Actions / GitLab CI 跑 AI Review
- pre-commit hook 跑基本检查
- **产出**：即使个人疏忽也被兜底

**大多数团队停在 Stage 2 或 Stage 3 就足够了。**

---

## 六、反面教材：过度设计的症状

如果你发现自己有以下症状，就是多 Agent 上早了：

- ❌ Agent 定义文件比业务代码还多
- ❌ 改一条规则要同步 5 个 Agent 的 Prompt
- ❌ Hooks 脚本报错比业务代码 Bug 还多
- ❌ AI 耗时从 2 分钟涨到 15 分钟（每个 Agent 反复读 Spec）
- ❌ 新人入门先学 5 个 Slash 命令
- ❌ 只有 1 个人能维护 Agent 定义

**退回 Stage 2 重新来**。

---

## 七、判断清单

回答下面 10 个问题，打分决策：

```
1. 团队 >5 人？                                    [+2]
2. 有明确的研发流程（需求→设计→编码→测试）？        [+2]
3. Spec 完整度 >80%（该写的都写了）？              [+2]
4. 单次任务平均耗时 >1 小时？                      [+1]
5. 多人同时开发（Git worktree 已在用）？           [+1]
6. 有专人维护工程化（不是纯业务团队）？             [+1]
7. AI 产出需要独立审查（安全/金融等高要求场景）？   [+2]
8. 有自动化测试覆盖（>60%）？                     [+1]
9. 熟悉 Hooks / MCP / Subagents 等概念？           [+1]
10. 愿意投入持续维护 Agent 定义？                  [+2]

总分：
0-5 分  → Stage 1-2 就够，别折腾
6-10 分 → 试试 Stage 3（Slash + 轻 Hooks）
11-15 分 → 可以上 Stage 4 多 Agent 流水线
```

---

## 八、一句话决策

> **如果你还在问「要不要多 Agent」，答案就是"先不要"。**
> **把 Spec 写好、把清单用好、把日志留好，等 AI 产出让你觉得"如果有人帮我审/分一下会更好"，再引入下一阶段。**
