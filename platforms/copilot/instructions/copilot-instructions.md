# GitHub Copilot — AIES Instructions

> 这个文件被 GitHub Copilot Chat 自动加载（放在 `.github/copilot-instructions.md` 或 workspace 根）。

## 项目规范

本项目采用 AIES (AI Engineering Scaffold)。所有代码建议必须遵循：

- 架构约束：见 `.aies/spec/architecture.md`
- 代码风格：见 `.aies/spec/code-style.md`
- 质量门：见 `.aies/spec/quality-gates.md`
- 错误处理：见 `.aies/spec/error-handling.md`
- 项目地图：见 `.ai/index.md`

## 关键要求

1. **Update 请求使用指针/可选类型**（区分"不传"和"传 null"）
2. **结构化字段注释**（含义 + 枚举值 + 默认值 + 约束）
3. **错误统一处理**（使用项目 errno / 错误码，不用 `fmt.Errorf` / `throw new Error('xxx')` 原生错误）
4. **日志结构化**（key-value 字段，不拼接字符串）
5. **context 全链路透传**（跨层调用必须透传上下文）

## 禁止

- 硬编码 URL、端口、密钥
- SQL 字符串拼接
- 静默吞掉错误
- 跳过鉴权校验
