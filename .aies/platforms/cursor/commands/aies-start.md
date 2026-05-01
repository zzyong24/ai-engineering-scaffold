# aies-start

初始化 AIES 会话。（`start` 是本命令的短别名）

## 执行步骤

1. 运行 `python3 .aies/scripts/session.py get-context` 获取开发者/任务/git 状态
2. 读取 `.aies/workflow.md`、`.aies/spec/index.md`、`.aies/.ai/index.md`
3. 如存在 `.aies/spec/guides/index.md`，读取并展示可用 Thinking Guides
4. 如有活跃任务，提示其 context.jsonl 中声明的 spec 范围
5. 输出 session 初始化报告
6. 若有活跃任务，询问是否继续
