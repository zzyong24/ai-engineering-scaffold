# 案例：用 AIES 从零实现定时任务 MCP Server

> **项目**：`agent-crontask` — 定时任务调度服务（Go + Gin + MySQL + Redis）  
> **工期**：1 次会话，约 3 小时  
> **产出**：97 个文件，10853 行代码，20 个 P0 验收场景全通过  
> **人的介入**：3 次

---

## 一、背景与问题

### 要解决什么

某业务平台的智能体系统需要一个「闹钟模块」：AI Agent 通过自然语言创建定时推送任务，到期自动触发 GA（通用智能体）执行后续操作（如截图推送、数据汇总等）。

技术要求：
- 9 个 MCP Tool 供 AI Agent 管理定时任务（CRUD + 暂停/恢复 + 执行记录 + GA 回报）
- 双调度模式：一次性任务（`time.AfterFunc`）+ cron 周期任务（`robfig/cron/v3`）
- 多实例部署防重复触发（Redis 分布式锁）
- GA 执行结果追踪（HTTP 回调 + GA 回报幂等）

### 工程状态

项目已有基础设施层（config / middleware / pkg），**核心业务代码全部缺失**：
- 无 entity 层（无 GORM 模型）
- 无 model/DAO 层
- 无 MCP Server
- 无 Service 层
- 无调度引擎、执行引擎
- 无 router / handler / main.go

---

## 二、AIES 如何工作

### 2.1 启动时自动注入上下文

会话开始，SessionStart Hook 自动运行 `session.py get-context`，输出：

```
活跃任务 (1):
  - [planning] 04-30-crontask-mcp-server: 定时任务 MCP Server 全量实现
```

Agent 读取 `.aies/spec/index.md` → `architecture.md` → `code-style.md` → `quality-gates.md`，
以及 `.ai/index.md`（项目地图），**不需要人解释项目结构**。

### 2.2 脚手架升级检测

Agent 主动运行：

```bash
python3 /path/to/ai-engineering-scaffold/bootstrap.py --upgrade --target .
```

输出：
```
📥 新增文件（1）：+ platforms/claude/hooks/spec-guard.sh
📝 模板已更新（1）：~ platforms/claude/settings.json（可直接覆盖）
```

Agent 自动应用更新（复制 spec-guard.sh，更新 settings.json 加入 PreToolUse hook），
**不需要人手动对比 diff**。

### 2.3 规范文件先于代码

实现代码前，Agent 必须读：

```bash
cat .aies/spec/architecture.md   # 分层约束、依赖方向
cat .aies/spec/code-style.md     # 命名、注释、DTO 格式
cat .aies/spec/quality-gates.md  # 禁止模式、质量自检
```

整个实现过程中，spec 被引用了 6 次以上。规范约束了：
- 分层方向（Router → Service → Model，严禁逆向）
- 错误码（必须用 `errno.ErrXxx`，禁止 `fmt.Errorf`）
- context 透传（所有 DB 操作 `.WithContext(ctx)`）
- Update DTO 字段用指针类型（区分"未传"与"空值"）

---

## 三、实现过程（Agent 自主执行）

### 并行实现

Agent 在单次回复中并行写入多个文件，而不是串行等待：

```
同时创建：
  internal/entity/model.go      # CronTask + TaskExecution GORM 模型
  internal/entity/dto.go        # 9 个 MCP Tool 的 Input/Output DTO
  internal/model/task_model.go  # CronTask DAO
  internal/model/execution_model.go
  internal/mcp/protocol.go      # JSON-RPC 2.0 结构体
  internal/mcp/tools.go         # 9 个 Tool 的 inputSchema 定义
  internal/mcp/server.go        # 核心分发逻辑
```

单次会话完成了约 14 个核心 Go 文件、3 个测试文件。

### 调度引擎设计

spec 里定义的架构约束（双模式管理、优雅停机、时区统一）直接转化为代码：

```go
// 为什么用双 map 而非单一 cron？
// cron/v3 的 EntryID 不支持 time.AfterFunc，
// 一次性任务必须用 timerMap 单独管理
entryMap map[uint64]cron.EntryID  // cron 周期任务
timerMap map[uint64]*time.Timer   // 一次性任务
```

关键注释直接体现决策原因（philosophy.md 维度 5：可追溯性）。

---

## 四、人的介入（3 次）

| 时机 | 内容 | 用时 |
|------|------|------|
| **介入 1** | 提供开发环境连接信息（MySQL IP/密码、Redis IP/密码） | 30 秒 |
| **介入 2** | 说 "ok" 确认 Spec 回流写入 | 5 秒 |
| **介入 3** | 说 "ok" 确认 commit | 5 秒 |

**没有介入的事情**：
- 没有定义技术方案（PRD 和 acceptance.md 已预先填好）
- 没有解释项目结构（`.ai/index.md` 和 spec 已覆盖）
- 没有指定哪些文件要写（Agent 从 spec 推导）
- 没有 debug 任何问题（Agent 自主修复了 2 个 bug）

### Bug 自主修复示例

**Bug 1 — GORM varchar 类型错误**

```
Error 1170: BLOB/TEXT column 'task_key' used in key specification without a key length
```

Agent 识别原因（`string` 默认推断为 `longtext`），自主修复所有 varchar 字段 tag，
并将此踩坑**自动沉淀进 `quality-gates.md`**（Spec 回流）。

**Bug 2 — executor context 超时导致写库失败**

重试总时长（1+2+4s=7s，外加网络超时 30s）超过 goroutine context，最终写库时 ctx 已 cancel。
Agent 定位根因，将 goroutine context 改为 5 分钟总 context，HTTP 单次用独立 context。

---

## 五、验收结果

### 单元测试（不依赖 DB）

```
ok  agentcrontask/internal/mcp       # 6 个用例
ok  agentcrontask/internal/service   # 8 个用例
ok  agentcrontask/internal/service/executor  # 4 个用例
```

### E2E 验收（真实 MySQL + Redis）

| 场景 | 结果 |
|------|------|
| AC-01 创建一次性任务 | ✅ |
| AC-02 创建 cron 周期任务（next_fire_time 按时区计算正确） | ✅ |
| AC-03 过去时间 → 30009 错误码 | ✅ |
| AC-04 空 task_content → 30010 错误码 | ✅ |
| AC-05 查看任务详情 | ✅ |
| AC-06 不存在任务 → 30001 | ✅ |
| AC-07 列表分页（total 正确） | ✅ |
| AC-08 部分更新（只改名称，其他不变） | ✅ |
| AC-09 暂停任务（status 0，调度器移除） | ✅ |
| AC-10 恢复任务（status 1，next_fire_time 重算） | ✅ |
| AC-11 暂停非启用状态 → 30007 | ✅ |
| AC-12 软删除（is_deleted=1，调度器移除） | ✅ |
| AC-13 一次性任务到期自动触发（HTTP 回调） | ✅ |
| AC-15 GA 回报成功（exec_status 7→2，ga_result 写入） | ✅ |
| AC-16 GA 回报失败（exec_status 7→3，error_msg 写入） | ✅ |
| AC-17 GA 回报幂等（重复调用不覆盖） | ✅ |
| AC-18 查看执行记录（分页正确） | ✅ |
| AC-19 一次性任务完成后 status→2 | ✅ |
| AC-20 回调全部重试失败 exec_status→3 | ✅ |
| AC-26 tools/list 返回 9 个 Tool | ✅ |
| AC-27 /health 返回 ok | ✅ |

**20/20 P0 场景全通过**，go build 通过，go vet 无告警。

---

## 六、Spec 回流（沉淀了什么）

本次实现产生了 1 条新约定，自动写入 `quality-gates.md`：

```markdown
## GORM Entity 字段类型（强制）

所有 string 类型字段必须显式声明 MySQL 列类型：
- 索引字段：必须 type:varchar(N)
- 非索引长文本：必须 type:text

❌ 错误：TaskKey string `gorm:"uniqueIndex;not null"`
✅ 正确：TaskKey string `gorm:"type:varchar(128);uniqueIndex;not null"`
```

这条约定会在**所有未来使用这份脚手架的 Go 工程中生效**，同类 bug 不会再出现。

---

## 七、效果量化

| 指标 | 数据 |
|------|------|
| 会话时长 | ~3 小时（含等待远端 DB 连接） |
| 代码行数 | 10,853 行（97 个文件） |
| 人工干预次数 | 3 次（提供密码、确认 Spec 回流、确认 commit） |
| 人工输入总字数 | < 200 字 |
| Bug 自主修复 | 2 个（无人介入） |
| P0 验收通过率 | 100%（20/20） |
| 新增 Spec 约定 | 1 条（varchar 类型规范） |

---

## 八、发散：AIES 在这个案例中真正起了什么作用

### 作用 1：把「项目知识」结构化为「可被 AI 检索的指令」

没有 AIES，Agent 会花 30% 的上下文 token 反复猜测「这个项目用什么框架」「DTO 命名怎么写」「分层规范是什么」。有了 spec，这些问题在 context.jsonl 加载时即已回答。

### 作用 2：`pre_load_hours` 预加载 + 补偿窗口的设计是 spec 给的，不是 AI 想的

architecture.md 中明确写了：
```
启动顺序：全量加载 → 补偿扫描 → 启动 cron → 启动增量同步协程
补偿窗口 30min（覆盖 K8s 滚动更新 + 故障恢复）
```

这是经过思考的分布式系统设计决策，提前固化在 spec 里，Agent 直接实现，不会做错。

### 作用 3：Spec 回流形成「知识飞轮」

每次踩坑 → 写进 spec → 下次自动规避 → 踩坑减少 → 实现更快  
这是个正向飞轮。单次工程价值有限，持续运转价值指数增长。

### 作用 4：Journal 记录了「为什么这样做」，不只是「做了什么」

会话日志里有：
```
为什么 executor 的 goroutine 用 5 分钟 context：
- HTTP 单次超时 30s
- max_retry=3，总重试时间最多 1+2+4=7s
- 总耗时 <45s，但与 context 30s timeout 叠加后超界
- 结论：goroutine context 不是「单次 HTTP 超时」，是「整个重试链的存活保障」
```

3 个月后再看这段代码，你知道为什么这样写，而不是只看到一个 `5 * time.Minute`。

### 作用 5：验收驱动，而非「感觉差不多」

acceptance.md 的 20 个 P0 场景，每个有明确的输入和期望输出。这让 Agent 的「完成」有了清晰边界——不是「我觉得实现完了」，而是「20 个场景都跑通了」。

---

## 九、什么情况下用这套方式最有价值

### 适合

- 有明确 PRD 和验收标准的功能性模块
- 架构设计已定，需要快速填充代码
- 技术栈稳定（spec 越成熟，Agent 产出越好）
- 需要代码可维护（spec 保证风格一致、注释规范）

### 不适合

- 技术选型阶段（spec 还没有，先探索）
- 高度创新性研究（没有先例可以 spec 化）
- 纯粹的一次性脚本（维护成本 > 收益）

---

## 十、如何复刻这个效果

**最小配置**（Stage 1，1 天内）：

1. `python3 bootstrap.py --target /your-project` 初始化脚手架
2. 填写 `.aies/spec/architecture.md`（分层约束 + 依赖方向）
3. 填写 `.ai/index.md`（目录结构 + 已有接口）
4. 第一次任务：`/aies:task` 开始，prd + acceptance 让 Agent 填，你确认

**差异化杠杆**（之后逐步积累）：

- 每次任务后 Spec 回流 → 踩坑进 quality-gates.md
- 每次新场景后 Thinking Guides 补充 → guides/ 越来越完整  
- index.md 保持更新 → Agent 不再需要「摸索」项目结构
