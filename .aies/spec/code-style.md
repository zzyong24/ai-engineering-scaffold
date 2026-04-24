# 代码风格规范

> 本文件定义项目的代码风格。AI 生成代码必须遵循。

---

## 命名规范

### 通用原则

- **语义清晰 > 简短**：`userRepository` > `ur`
- **避免歧义词**：不用 `data`、`info`、`obj`、`temp`
- **专有名词保持大小写**：`UserID`（Go）、`userId`（TS）

### 按类型命名

> 根据项目语言调整

| 类型 | 规则 | 示例 |
|------|-----|------|
| 常量 | UPPER_SNAKE_CASE | `MAX_PAGE_SIZE` |
| 变量/函数 | 按语言约定 | Go: camelCase / TS: camelCase |
| 类/结构体 | PascalCase | `AgentService` |
| 接口 | PascalCase（可加 I 前缀） | `IAgentRepository` 或 `AgentRepository` |
| 枚举值 | PascalCase | `StatusActive` |
| 文件 | 按语言约定 | Go: snake_case / TS: kebab-case |

---

## 注释规范（强制）

### 结构体 / DTO 字段必须有结构化注释

```
含义 + 枚举值 + 默认值 + 约束
```

✅ 正确：
```go
// Temperature 温度参数，控制输出随机性。范围：0.0~2.0，默认值：0.7
Temperature float64 `json:"temperature"`

// Status 状态。枚举值：draft（草稿）/active（启用）/inactive（停用）/archived（归档）
Status string `json:"status"`

// Args 启动参数（JSON 数组格式字符串）。示例：'["server.js","--port","3000"]'
Args string `json:"args"`
```

❌ 错误：
```go
// Temperature 温度
Temperature float64  // ← 无范围、无默认值

// Status 状态
Status string  // ← 无枚举值说明
```

### 函数/方法注释

✅ 正确：
```
// CreateAgent 创建智能体
// @param ctx 请求上下文（用于超时/追踪）
// @param req 创建请求
// @return *AgentResponse 创建的智能体
// @return error 业务错误（errno.ErrXXX）或系统错误
```

### 复杂逻辑必须有决策注释

```go
// 这里使用乐观锁而非悲观锁：
// - 冲突率 <5%（业务数据）
// - 失败可以由用户重试，无需阻塞
// - 避免 MySQL 死锁问题
tx.Where("version = ?", oldVersion).Updates(...)
```

---

## 禁止模式

### ❌ 禁止 1：魔法数字

```
// ❌ 错误
if pageSize > 100 { pageSize = 100 }

// ✅ 正确：常量放在 constant 目录
const MaxPageSize = 100
if pageSize > MaxPageSize { pageSize = MaxPageSize }
```

### ❌ 禁止 2：静默吞掉错误

```
// ❌ 错误
_ = someFunc()

// ✅ 正确
if err := someFunc(); err != nil {
    logger.Error(ctx, "xxx failed", zap.Error(err))
    return errno.ErrXxx
}
```

### ❌ 禁止 3：拼接字符串构造 SQL

```
// ❌ 禁止（SQL 注入）
db.Where("name = '" + name + "'")

// ✅ 正确（参数化）
db.Where("name = ?", name)
```

### ❌ 禁止 4：硬编码敏感信息

```
// ❌ 错误
secret := "my-secret-key-123"

// ✅ 正确
secret := config.JWTSecret  // 来自配置
```

---

## 必须模式

### ✅ 必须 1：Update DTO 用指针类型（或可选类型）

区分「不传」和「传 null」：

Go:
```go
type UpdateRequest struct {
    Name   *string  `json:"name"`   // 指针
    Amount *float64 `json:"amount"` // 指针
}
```

TypeScript:
```typescript
interface UpdateRequest {
    name?: string | null;   // 可选 + 可空
    amount?: number | null;
}
```

### ✅ 必须 2：错误使用项目统一错误码

TODO: 按项目约定填写

### ✅ 必须 3：日志使用结构化字段

```
// ❌ 错误
log.Printf("user %s login failed: %v", userID, err)

// ✅ 正确（可被日志平台索引）
logger.Error(ctx, "user login failed",
    zap.String("user_id", userID),
    zap.Error(err),
)
```

### ✅ 必须 4：时间字段统一 UTC

```
// 存储时用 UTC
time.Now().UTC()

// 展示时按前端时区转换（不在后端 convert）
```

---

## 函数长度限制（建议）

- 单个函数 ≤ 80 行
- 超过时拆分为子函数
- 单行长度 ≤ 120 字符

---

## 项目特定风格

TODO: 各项目补充特有风格，如：
- Swagger 注释规则
- 特定的 lint 规则
- 国际化字段命名
