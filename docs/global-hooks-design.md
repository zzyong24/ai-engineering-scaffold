# 全局 Hook 设计指南：在 Claude Code 中自动记录重大产出

> 本文是 AIES 的**延伸设计**，讲如何在 Claude Code 全局 hooks 中实现「重大产出自动记录」。
> 这个能力**不应放进工程脚手架**（因为依赖个人工具），而应放在 `~/.claude/settings.json` 全局配置。

---

## 一、问题背景

工程级的 session journal（`.aies/workspace/{dev}/journal.md`）解决了「跨会话接续」的问题，
但有个缺口：**重大产出没有被沉淀到个人知识库**。

比如这种情况：
- 用 1 次会话从零实现了一个 MCP Server
- 踩了 2 个坑（GORM varchar、executor context 超时）
- 这些经验只在项目的 journal 里，不在个人的知识积累里

「个人工作日志」和「项目会话日志」是两个不同的层次：

| | 工程 journal | 个人 worklog |
|--|-------------|-------------|
| 位置 | `.aies/workspace/{dev}/journal-N.md` | 个人知识库/vault |
| 读者 | AI（下次接续上下文） | 人（回顾/沉淀） |
| 触发时机 | 每次会话结束自动追加 | 有重大产出时触发 |
| 内容粒度 | 技术细节（commit hash、文件改动） | 决策理由、踩坑、经验 |

---

## 二、设计原则

### 原则 1：仅在有实质产出时触发

不要每次 `claude` 停止都触发，那会让人觉得烦。只在以下情况触发：

- 最近 60 分钟内有 `git commit`
- AIES 任务状态变为 `completed`
- Stop hook 收到的 stdin 包含「完成类关键词」（completed / 验收通过 / commit / deploy）

### 原则 2：降级优雅

停止 hook 的 target 用户可能：
- 没有个人知识库（VAULT 不存在）→ 直接放行
- 有 VAULT 但没有特定 MCP 工具 → Claude 直接写文件兜底
- 有完整工具链 → 调用 MCP 工具自动化处理

不要因为没有某个工具就让 hook 报错或死锁。

### 原则 3：防死循环

Stop hook 触发 → Claude 写日志 → Claude 停止 → 再次触发 Stop → ...

解法：**LOCK_FILE 机制**。Claude 完成日志写入后再次触发 Stop 时，检测到锁文件存在，立即删锁并放行。

### 原则 4：最多每 2 小时触发一次兜底记录

即使没有重大产出，也应该有频次上限的日常记录。建议：
- 有重大产出：立即触发（但每次产出只触发一次）
- 无重大产出：每天最多触发 1 次兜底记录（或每 2 小时一次）

---

## 三、实现模板

在 `~/.claude/settings.json` 中：

```json
{
  "hooks": {
    "Stop": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "~/.claude/hooks/session-stop.sh",
            "timeout": 10000,
            "statusMessage": "检查是否需要记录工作日志..."
          }
        ]
      }
    ],
    "PreCompact": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "~/.claude/hooks/session-stop.sh",
            "timeout": 10000,
            "statusMessage": "上下文压缩前保存记录..."
          }
        ]
      }
    ]
  }
}
```

**核心 shell 逻辑**（`~/.claude/hooks/session-stop.sh`）：

```bash
#!/bin/bash
# 防死循环
LOCK="$HOME/.claude/hook_state/stop_active.flag"
if [ -f "$LOCK" ]; then rm -f "$LOCK"; echo "{}"; exit 0; fi

# 检测重大产出
HAS_MAJOR=false
if git -C "${PWD:-$HOME}" log --oneline --since="60 minutes ago" 2>/dev/null | grep -q .; then
    HAS_MAJOR=true
fi
# 可以加更多检测逻辑...

if [ "$HAS_MAJOR" = true ]; then
    touch "$LOCK"
    cat << 'EOF'
{
  "decision": "block",
  "reason": "检测到重大产出，请记录工作日志后停止。
  优先使用你的 auto_worklog / append_worklog 工具；
  如果没有这类工具，请直接在对话中总结关键决策和踩坑。"
}
EOF
    exit 0
fi

echo "{}"
```

---

## 四、关键设计决策说明

### 为什么用 Stop hook 而不是 PostToolUse？

Stop hook 是整个会话的收尾点，适合做「全局总结」。  
PostToolUse 在每个工具调用后触发，粒度太细，容易打断 AI 的工作流。

### 为什么是 block 而不是 nonblock？

`nonblock` 不支持给 Claude 传指令（reason 字段只在 block 时生效）。  
如果只是想让 Claude「顺带写一句」，`block` + 简短 reason 是目前唯一有效方式。

### 为什么记录工具应该放在全局 hook 而不是工程脚手架？

工程脚手架的 hooks（如 `spec-guard.sh`）是**工程级约束**，适合所有使用该工程的人。  
个人知识库工具（如 `auto_worklog`、`append_worklog`）是**个人工具**，不同人的工具链不同。  
混在一起会导致：别人 clone 工程后 hook 报错，体验很差。

**原则**：工程工具放工程，个人工具放全局。

### 为什么要有 VAULT 检测？

没有个人知识库的用户（纯代码工程用户）不需要工作日志功能。  
强行触发只会让 hook 报错或 Claude 无所适从。有 VAULT 意味着有「记录习惯」，才触发。

---

## 五、扩展：其他值得放进全局 hook 的场景

| 场景 | Hook 类型 | 触发条件 | 动作 |
|------|---------|---------|------|
| 重大产出记录 | Stop | git commit / 任务完成 | 调用个人日志工具 |
| 安全检查 | PreToolUse (Write/Edit) | 文件路径含 `.env` / `credentials` | block + 警告 |
| 敏感文件保护 | PreToolUse (Bash) | 命令含 `rm -rf` / `DROP TABLE` | block + 二次确认 |
| 上下文压缩前备份 | PreCompact | 总是 | 触发与 Stop 相同的日志逻辑 |
| 代码统计 | Stop | 总是（nonblock） | 统计今日 AI 辅助写了多少行 |

---

## 六、与工程 journal 的关系

```
工程 journal（.aies/workspace/{dev}/journal-N.md）
  ↓ 自动追加（每次会话结束）
  包含：技术细节、commit hash、文件路径、API 变更

全局 worklog（~/vault/space/crafted/work/worklog/...）
  ↑ 按需触发（有重大产出时）
  包含：决策理由、踩坑经验、项目进展、个人感受

两者互补，不重复。
journal 给 AI 读（接续上下文）
worklog 给人读（成长积累）
```
