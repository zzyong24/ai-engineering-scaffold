# {{PROJECT_NAME}} — Claude Code 规范入口

> 本文件是 Claude Code 在本项目中的强制规范入口。所有代码生成行为必须先加载下述文件。

---

## 必读文件（每次会话开始）

Claude Code 的 SessionStart Hook 会自动注入以下文件，无需手动读取：

1. `.aies/workflow.md` —— 工作流（Phase 1/2/3 协议）
2. `.aies/spec/index.md` —— 规范导航
3. `.ai/index.md` —— 项目地图
4. `.ai/review-checklist.md` —— 审查清单

如未启用 Hook，请 AI 在对话开始时**主动读取**上述文件。

---

## 每次任务的强制协议

### Phase 1：启动清单（写代码前第一段输出）

```
📋 任务启动清单
━━━━━━━━━━━━━━
• 任务类型：[新增 / 修改 / 修复 / 重构 / 其他]
• 需读取的参考文件：[按 .ai/context-guide.md 列出]
• 涉及的规范要点：[从 .aies/spec/ 列出]
• 预计变更文件：[列出]
• 索引需更新：[是 / 否]
```

### Phase 2：执行

按清单读取参考文件 → 生成代码。

### Phase 3：完成清单（写完代码后必须输出）

```
✅ 任务完成清单
━━━━━━━━━━━━━━
1. 质量自检（参照 .ai/review-checklist.md）
2. 索引更新：[.ai/index.md 已更新 / 无需]
3. 建议 commit message：`type(scope): 描述 [ai-assisted]`
4. 会话日志：python3 .aies/scripts/session.py add --title "..." --summary "..."
5. Spec 缺口：[有/无新约定需沉淀]
```

---

## Slash 命令

| 命令 | 作用 |
|------|------|
| `/aies:start` | 初始化会话（读上下文 + 规范） |
| `/aies:finish-work` | 完成清单 |
| `/aies:new-feature` | 按 new-feature.md 模板执行 |
| `/aies:fix-bug` | 按 fix-bug.md 模板执行 |
| `/aies:review` | 按 code-review.md 模板执行 |
| `/aies:commit` | 按 git-commit.md 模板执行 |

---

## 多 Agent（可选）

如启用 `.aies/config.yaml` 中 `multi_agent.enabled: true`：

- `dispatch` —— 调度器
- `plan` —— 方案设计
- `implement` —— 实现
- `check` —— 审查 + 自修复
- `debug` —— 调试

详见 `.claude/agents/` 下各 Agent 定义。

---

## 禁止事项

- ❌ 跳过 Phase 1 直接写代码
- ❌ `git commit/push/merge` 未经用户确认
- ❌ 编造项目中不存在的函数/类型（必须先读 `.ai/index.md`）
- ❌ 大段重写用户未要求的代码
