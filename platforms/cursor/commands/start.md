# start

初始化 AIES 会话。等同于 `aies-start`，更短的别名。

## 执行步骤

1. 运行 `python3 .aies/scripts/session.py get-context` 获取开发者/任务/git 状态
2. 读取 `.aies/workflow.md`、`.aies/spec/index.md`、`.ai/index.md`
3. 如存在 `.aies/spec/guides/index.md`，提示本次任务应参考哪些 thinking guides
4. 输出 session 初始化报告
5. 若有活跃任务，询问是否继续
