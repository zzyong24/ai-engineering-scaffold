---
description: AIES (AI Engineering Scaffold) — Agent 驱动的上下文体系（CodeBuddy 自动加载）
alwaysApply: true
enabled: true
---

# {{PROJECT_NAME}} — CodeBuddy AI 规范

> 定位：人描述意图，Agent 驱动执行。人在两个节点拍板：确认 prd+acceptance、确认 Spec 回流。

---

## Agent 工作模式（最高优先级）

收到用户描述后，**自己判断该做什么**：

| 用户说 | Agent 做 |
|--------|---------|
| 新需求/实现X/加Y | 意图解析 → 填 prd+acceptance → 提议 → 确认 → 实现 |
| 继续/上次/那个任务 | 读 journal 接续，直接实现 |
| 完成/收尾/done | Phase 3 + Spec 回流 + 日志 |
| 初始化/setup | 询问3问 → 运行 bootstrap → 填 index.md |
| 进度/状态 | task list + journal 摘要 |

## 提议协议

```
❌ 问卷式："请问您需要什么？"
✅ 提议式："我的理解是X，验收标准是[3条]，说ok开始。"
```

## 任务完成清单（强制）

```
✅ Phase 3 完成清单
1. 对照 acceptance.md P0 场景确认
2. review-checklist.md 9 大维度自检
3. 更新 .ai/index.md（如有新增）
4. ⭐ Spec 回流（必须显式回答，不能沉默）：
   Q1: 有统一规范的地方吗？
   Q2: 有踩坑要记录吗？
   Q3: guides/ 需要新增吗？
   → 有 → 展示 diff 等确认 → 写入 spec + changelog
   → 无 → 明确写"Spec 回流：无新约定"
5. 日志：python3 .aies/scripts/session.py add ...
```

## 上下文体系

```
.aies/spec/         规范（architecture/code-style/quality-gates/...）
.aies/spec/guides/  Thinking Guides（code-reuse/cross-layer/auth-context）
.ai/index.md        项目地图（禁止编造里面没有的函数/类型）
.aies/tasks/        任务目录（prd/acceptance/context.jsonl — Agent 填写）
.aies/workspace/    跨会话记忆（journal）
```

## 禁止

- ❌ 编造 .ai/index.md 中不存在的函数/类型
- ❌ Spec 回流沉默跳过
- ❌ acceptance.md 留 TODO
- ❌ git commit 未经用户明确说"提交"
- ❌ 跳过 prd+acceptance 提议直接开始实现
