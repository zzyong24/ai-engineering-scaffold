# Codex CLI / Generic Agents — AIES Entry

> 本文件是 Codex CLI、通用 AI Agent 在本项目中的入口。

## 必读文件

按顺序加载：

1. `.aies/workflow.md` — 工作流（含 Phase 1/2/3 协议）
2. `.aies/spec/index.md` — 规范导航
3. `.ai/index.md` — 项目地图
4. `.ai/review-checklist.md` — 审查清单

## 强制协议

所有任务必须：
1. 先输出 Phase 1 启动清单
2. 执行
3. 输出 Phase 3 完成清单

详见 `.aies/workflow.md`。

## 上下文与任务

```bash
# 查看当前上下文
python3 .aies/scripts/session.py get-context

# 任务管理
python3 .aies/scripts/task.py list
python3 .aies/scripts/task.py create "标题" --slug xxx

# 记录会话
python3 .aies/scripts/session.py add --title "..." --summary "..."
```
