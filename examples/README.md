# AIES 示例项目

本目录存放针对不同语言/框架的 AIES 定制示例（Spec 已按语言填写）。

## 计划支持

- `go-gin/` —— Go + Gin + GORM + MySQL 四层架构（参考 agent-manage-backend）
- `typescript-nest/` —— TypeScript + NestJS + TypeORM
- `python-fastapi/` —— Python + FastAPI + SQLAlchemy
- `rust-axum/` —— Rust + Axum
- `java-spring/` —— Java + Spring Boot

## 使用

每个示例是完整的 `.ai/` + `.aies/` 模板组合，你可以：

```bash
# 基于示例初始化
python3 bootstrap.py --target /path/to/new-project \\
    --from-example go-gin --developer your-name
```

（`--from-example` 功能在 roadmap 中，当前手动拷贝即可）

## 贡献

欢迎提 PR 添加新的语言/框架示例。每个示例应包含：
- 完整的 `.ai/` 目录（含填好的 index.md）
- 完整的 `.aies/spec/` 目录（语言特定规范）
- 示例 `Makefile` / `package.json` 命令
- 一段简单的业务代码（演示规范落地）
