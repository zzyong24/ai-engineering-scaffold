# 架构规范

> 本文件定义项目的架构约束。**所有代码生成必须遵守**。
> 自动生成于 2026-05-01

---

## 分层架构

### Python + fastapi 项目结构

```
│  （未检测到分层结构）
```

### 依赖方向

**严格单向**：入口层 → 业务层 → 数据层

**严禁**：
- ❌ 数据层依赖业务层
- ❌ 入口层跳过业务层直接访问数据层
- ❌ 业务层依赖具体入口层（如 HTTP 框架）

---

## 目录结构

```
├── ci/
├── docs/
├── examples/
├── platforms/
```

### 文件命名约定

Python 风格：
- 文件：`{layer}_{entity}.py`（如 `service_agent.py`、`repository_user.py`）
- 类：`AgentService`、`UserRepository`（大写驼峰）

---

## 依赖注入规范

**Python 典型 DI 方式**：构造函数注入。

示例：

```python
class AgentService:
    def __init__(
        self,
        agent_repo: AgentRepository,
        logger: Logger,
    ) -> None:
        self._agent_repo = agent_repo
        self._logger = logger

    async def create_agent(self, req: CreateAgentDto) -> Agent:
        return await self._agent_repo.create(req)
```

---

## 上下文透传规范（强制）

**所有跨层调用必须透传 context**：

```
入口层获取 ctx → 透传到业务层 → 透传到数据层 → 数据层的所有 I/O 操作使用 ctx
```

**为什么强制**：
- 超时控制
- 链路追踪（trace_id）
- 请求取消
- 日志关联（user_id、request_id）

---

## 关键约束

### 约束 1：单一职责

每个函数/类只做一件事。参数超过 4 个 → 封装为 struct。

### 约束 2：开闭原则

对扩展开放，对修改关闭。新增功能优先通过新增文件，避免修改核心逻辑。

### 约束 3：显式优于隐式

- 错误必须显式处理，不得静默吞掉
- 配置必须显式声明，不得依赖环境变量默认行为
- 类型必须显式标注（弱类型语言尤其重要）

---

## 项目特定规范

> 本项目使用 Python + fastapi。
> 更多规范参见 `code-style.md`。
