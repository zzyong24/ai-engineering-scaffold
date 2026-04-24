# {{PROJECT_NAME}} 规范索引

> 所有 AI 开发任务**必须**在写代码前先阅读相关 Spec 文件。
>
> 本文件是规范导航，按任务类型选择性读取，遵循「最小充分上下文」原则。

---

## 项目概览

| 项 | 值 |
|----|-----|
| 技术栈 | TODO: 填写语言/框架版本 |
| 架构模式 | TODO: 填写分层模式 |
| 最后更新 | {{LAST_UPDATED}} |

---

## Spec 清单

| Spec | 适用场景 | 必读时机 |
|------|---------|---------|
| [architecture.md](./architecture.md) | 架构约束、分层职责 | **每次写代码前** |
| [code-style.md](./code-style.md) | 命名、注释、格式 | **每次写代码前** |
| [quality-gates.md](./quality-gates.md) | 禁止模式、必须模式、自检清单 | **每次写代码前** |
| [error-handling.md](./error-handling.md) | 错误处理、错误码规范 | 涉及错误处理时 |
| [logging.md](./logging.md) | 日志级别、格式、敏感字段 | 涉及日志时 |

---

## 开发前必读清单

```bash
# 每次任务开始前按顺序读取：
cat .aies/spec/index.md              # 本文件
cat .aies/spec/architecture.md       # 架构约束
cat .aies/spec/code-style.md         # 代码风格
cat .aies/spec/quality-gates.md      # 质量门

# 按任务类型额外读取：
# 涉及错误处理 → error-handling.md
# 涉及日志     → logging.md
```

---

## 任务启动检查清单

```
📋 任务启动清单
━━━━━━━━━━━━━━
• 任务类型：[新增 / 修改 / 修复 / 重构 / 其他]
• 需读取的参考文件：[按 .ai/context-guide.md 列出]
• 涉及的规范要点：[从本目录下各 Spec 列出]
• 预计变更文件：[列出]
• 索引需更新：[是 / 否]
```

---

## 任务完成检查清单

```
✅ 任务完成清单
━━━━━━━━━━━━━━
1. 质量自检（逐项打勾）：
   - [ ] 架构合规（分层、依赖方向）
   - [ ] 代码风格（命名、注释、格式）
   - [ ] 错误处理（分类正确、使用统一错误码）
   - [ ] 安全检查（参数化、输入校验、无硬编码）
   - [ ] 日志规范（关键操作有日志、无敏感字段）
   - [ ] 编译/类型检查通过
2. 索引更新：[已更新 .ai/index.md / 无需更新]
3. 建议 commit message：`type(scope): 描述 [ai-assisted]`
4. 是否有新约定需沉淀到 Spec：[有/无]
```

---

## 规范维护规则

1. **发现新约定 → 24 小时内进入 Spec**
2. **修改 Spec 必须在 `.ai/changelog.md` 记录**
3. **Spec 使用「强制」/「建议」标签清晰区分**
4. **示例代码使用 ✅/❌ 对比呈现**
