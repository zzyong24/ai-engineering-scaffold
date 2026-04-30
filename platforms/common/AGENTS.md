# AGENTS.md — 通用 AI Agent 入口

> 定位：人描述意图，Agent 驱动执行。
> `.aies/` + `.ai/` 是 Agent 的上下文体系和跨会话记忆，不是给人看的文档。

---

## 启动检测

首先检测项目状态：

```bash
ls .aies/workflow.md 2>/dev/null || echo "UNINITIALIZED"
cat .aies/.developer 2>/dev/null
python3 .aies/scripts/session.py get-context 2>/dev/null
```

**未初始化** → 询问用户 3 个问题（名称/分层/平台），运行 bootstrap，引导填写 `.ai/index.md`。

**已初始化** → 展示活跃任务，等待用户描述意图。

---

## 意图路由

| 用户说 | Agent 做 |
|--------|---------|
| 新需求/实现X/加Y/修Z | 意图解析 → 填 prd+acceptance → 提议 → 确认 → 实现 |
| 继续/上次 | 读 journal 接续，直接实现 |
| 完成/收尾 | Phase 3 + Spec 回流 + 日志 |
| 初始化/setup | 运行 bootstrap 流程 |

---

## 提议协议

**提议而非询问**：Agent 基于意图生成 prd + acceptance，展示给用户确认，而不是反复问用户要什么。

```
我的理解：{一句话}
验收标准（{N}条）：{列表}
不确定点：{1-2个}
说"ok"开始，或告诉我哪里要改。
```

---

## 关键能力

```bash
# 获取当前上下文
python3 .aies/scripts/session.py get-context

# 创建任务（Agent 自动调用，用户不需要手动执行）
python3 .aies/scripts/task.py create "标题" --slug slug

# 完成后记录日志（Agent 自动执行）
python3 .aies/scripts/session.py add --title "..." --summary "..."

# 归档任务
python3 .aies/scripts/task.py finish {slug}
```

---

## 上下文体系

```
.aies/spec/index.md       规范导航（写代码前读）
.aies/spec/guides/        Thinking Guides（动手前按场景选读）
.ai/index.md              项目地图（禁止编造里面没有的内容）
.aies/tasks/{slug}/       任务目录（prd/acceptance/context.jsonl）
.aies/workspace/{dev}/    跨会话记忆
```

---

## 人必须拍板的两个点

1. **prd + acceptance 提议展示后** — 用户说"ok"才开始实现
2. **Spec 回流展示后** — 用户确认才写入 spec 文件

---

## 禁止

- ❌ 编造 `.ai/index.md` 中不存在的函数/类型
- ❌ 跳过 prd+acceptance 提议直接开始实现
- ❌ Spec 回流沉默跳过（必须显式回答三问）
- ❌ `git commit/push` 未经用户明确说"提交"
