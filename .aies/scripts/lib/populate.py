#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能填充模块：根据项目实际情况自动填充 AIES 规范文件
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

# ============================================================
# 语言与框架检测
# ============================================================

LANGUAGES = {
    "go": {"extensions": [".go"], "framework": ["gin", "echo", "fiber", "chi"], "files": ["go.mod"]},
    "typescript": {"extensions": [".ts", ".tsx"], "framework": ["nest", "next", "express", "fastify"], "files": ["package.json"]},
    "python": {"extensions": [".py"], "framework": ["fastapi", "flask", "django", "chalice"], "files": ["requirements.txt", "pyproject.toml", "setup.py"]},
    "java": {"extensions": [".java"], "framework": ["spring", "springboot"], "files": ["pom.xml", "build.gradle"]},
    "rust": {"extensions": [".rs"], "framework": ["actix", "rocket", "axum"], "files": ["Cargo.toml"]},
    "csharp": {"extensions": [".cs"], "framework": ["asp.net", "netcore"], "files": ["*.csproj"]},
}

SKIP_DIRS = {".git", "node_modules", "__pycache__", ".venv", "vendor", ".idea", ".vscode", "dist", "build"}


def detect_language(target: Path) -> str | None:
    """根据特征文件检测项目语言"""
    for lang, cfg in LANGUAGES.items():
        for f in cfg["files"]:
            if "*" in f:
                if any(target.rglob(f.replace("*", "*.csproj"))):
                    return lang
            else:
                if (target / f).exists():
                    return lang
    # fallback: 按扩展名统计
    ext_counts: dict[str, int] = {}
    for f in target.rglob("*"):
        if f.is_file() and f.suffix in [".go", ".ts", ".py", ".java", ".rs", ".cs"]:
            if not any(s in f.parts for s in SKIP_DIRS):
                ext_counts[f.suffix] = ext_counts.get(f.suffix, 0) + 1
    if not ext_counts:
        return None
    ext_to_lang = {".go": "go", ".ts": "typescript", ".tsx": "typescript", ".py": "python", ".java": "java", ".rs": "rust", ".cs": "csharp"}
    return ext_to_lang.get(max(ext_counts, key=ext_counts.get))  # type: ignore


def detect_framework(target: Path, language: str) -> str | None:
    """检测框架"""
    framework_markers: dict[str, list[str]] = {
        "go": ["github.com/gin-gonic", "github.com/labstack/echo", "github.com/gofiber"],
        "typescript": ["@nestjs", "next", "express", "fastify"],
        "python": ["fastapi", "flask", "django", "chalice"],
        "java": ["springframework", "springboot"],
    }
    markers = framework_markers.get(language, [])
    text_extensions = {".go", ".json", ".txt", ".py", ".java"}
    for marker in markers:
        for f in target.rglob("*"):
            if f.is_file() and f.suffix in text_extensions:
                if not any(s in f.parts for s in SKIP_DIRS):
                    try:
                        if marker in f.read_text(errors="ignore"):
                            return marker.split("/")[-1]
                    except Exception:
                        pass
    return None


def scan_directory_structure(target: Path) -> dict[str, list[str]]:
    """扫描目录结构"""
    result: dict[str, list[str]] = {"dirs": [], "files": []}
    for item in target.rglob("*"):
        if item.is_dir():
            rel = str(item.relative_to(target))
            if not any(s in rel.split("/") for s in SKIP_DIRS):
                result["dirs"].append(rel)
        elif item.is_file():
            rel = str(item.relative_to(target))
            if not any(s in rel.split("/") for s in SKIP_DIRS):
                result["files"].append(rel)
    return result


def detect_layers(dirs: list[str]) -> dict[str, str]:
    """根据目录结构推断分层"""
    detected: dict[str, str] = {}
    layer_keywords = {
        "cmd": "入口层（Main/CLI）",
        "internal/domain": "领域层",
        "domain": "领域层",
        "internal/service": "服务层",
        "service": "服务层",
        "internal/repository": "仓储层",
        "repository": "仓储层",
        "repositories": "仓储层",
        "api": "入口层（API）",
        "controllers": "入口层（Controller）",
        "handlers": "入口层（Handler）",
        "pkg": "公共库",
        "lib": "公共库",
        "models": "数据模型",
        "schemas": "数据模型",
        "middleware": "中间件",
        "config": "配置",
    }
    for d in dirs:
        for key, label in layer_keywords.items():
            if d.startswith(key + "/") or d == key:
                prefix = d.split("/")[0]
                detected_key = prefix + "/" + key if prefix != key else key
                if detected_key not in detected:
                    detected[detected_key] = label
    return detected


def has_meaningful_code(target: Path) -> bool:
    """检测是否有真实代码（排除空项目）"""
    code_exts = {".go", ".ts", ".tsx", ".py", ".java", ".rs", ".cs", ".js", ".jsx", ".c", ".cpp", ".h"}
    count = 0
    for f in target.rglob("*"):
        if f.is_file() and f.suffix in code_exts:
            if not any(s in f.parts for s in SKIP_DIRS):
                count += 1
    return count >= 3


# ============================================================
# 内容生成
# ============================================================

LANG_DISPLAY = {
    "go": "Go", "typescript": "TypeScript", "python": "Python",
    "java": "Java", "rust": "Rust", "csharp": "C#", "unknown": "Unknown"
}


def generate_architecture_md(language: str, framework: str | None, layers: dict[str, str], top_dirs: list[str]) -> str:
    """生成 architecture.md 内容"""
    lang_name = LANG_DISPLAY.get(language, language.title())
    fw_str = f" + {framework}" if framework else ""

    # 构建分层图
    layer_lines = []
    for layer_path, layer_name in sorted(layers.items()):
        layer_lines.append(f"│  {layer_name:<20} ({layer_path})")

    diagram = "\n".join(layer_lines) if layer_lines else "│  （未检测到分层结构）"

    # 目录结构
    dir_struct = "\n".join(f"├── {d}/" for d in sorted(top_dirs)[:12]) if top_dirs else "├── （空项目）"

    # 命名约定
    naming_templates = {
        "go": "Go 风格：\n- 文件：`{entity}_{layer}.go`（如 `agent_service.go`、`user_repository.go`）\n- 结构体：`AgentService`、`UserRepository`（大写驼峰）",
        "typescript": "TypeScript 风格：\n- 文件：`{entity}.{layer}.ts`（如 `agent.service.ts`、`user.controller.ts`）\n- 类：`AgentService`、`UserController`（大写驼峰）",
        "python": "Python 风格：\n- 文件：`{layer}_{entity}.py`（如 `service_agent.py`、`repository_user.py`）\n- 类：`AgentService`、`UserRepository`（大写驼峰）",
        "java": "Java 风格：\n- 文件：`{Entity}{Layer}.java`（如 `AgentService.java`、`UserRepository.java`）\n- 类：大写驼峰",
        "rust": "Rust 风格：\n- 文件：`{entity}_{layer}.rs`（如 `agent_service.rs`）\n- 结构体/枚举：`AgentService`、`UserRepository`（大写驼峰）",
    }
    naming = naming_templates.get(language, f"{lang_name} 风格")

    # DI 示例
    di_examples = {
        "go": '''```go\ntype AgentAPI struct {\n    agentService *service.AgentService\n}\n\n// 调用方式\nresult, err := a.agentService.CreateAgent(ctx, req)\n```''',
        "typescript": '''```typescript\nclass AgentService {\n  constructor(\n    private readonly agentRepo: AgentRepository,\n    private readonly logger: LoggerService,\n  ) {}\n\n  async createAgent(req: CreateAgentDto): Promise<Agent> {\n    return this.agentRepo.create(req);\n  }\n}\n```''',
        "python": '''```python\nclass AgentService:\n    def __init__(\n        self,\n        agent_repo: AgentRepository,\n        logger: Logger,\n    ) -> None:\n        self._agent_repo = agent_repo\n        self._logger = logger\n\n    async def create_agent(self, req: CreateAgentDto) -> Agent:\n        return await self._agent_repo.create(req)\n```''',
    }
    di_example = di_examples.get(language, "```\n// 使用构造函数注入\n```")

    date_str = datetime.now().strftime("%Y-%m-%d")

    return f"""# 架构规范

> 本文件定义项目的架构约束。**所有代码生成必须遵守**。
> 自动生成于 {date_str}

---

## 分层架构

### {lang_name}{fw_str} 项目结构

```
{diagram}
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
{dir_struct}
```

### 文件命名约定

{naming}

---

## 依赖注入规范

**{lang_name} 典型 DI 方式**：构造函数注入。

示例：

{di_example}

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

> 本项目使用 {lang_name}{fw_str}。
> 更多规范参见 `code-style.md`。
"""


def generate_code_style_md(language: str) -> str:
    """生成 code-style.md 内容"""
    date_str = datetime.now().strftime("%Y-%m-%d")

    go_style = f"""# 代码风格

> 本文件定义 Go 代码风格约束。
> 自动生成于 {date_str}

---

## 格式化

- 使用 `gofmt` / `goimports` 自动格式化
- 行长度：无硬限制，但单行尽量不超过 120 字符
- 缩进：4 空格（不用 Tab）

## 命名

### 包名

- 全部小写
- 简洁，不使用下划线
- 同一目录尽量一个包

### 变量/函数名

- 使用驼峰命名
- 导出：大写开头
- 不导出：小写开头

### 常量

- 全大写 + 下划线：`MAX_RETRIES`

## 错误处理

- 错误作为返回值，不得忽略（使用 `_` 显式忽略）
- 自定义错误：`fmt.Errorf("context: %w", err)`
- 禁止使用 `panic` 进行业务错误处理

## 导入

- 分三组：标准库、项目内部、第三方
- 使用 `goimports` 自动整理

## 注释

- 公共 API 必须有文档注释
- 注释以完整句子结尾
"""

    ts_style = f"""# 代码风格

> 本文件定义 TypeScript 代码风格约束。
> 自动生成于 {date_str}

---

## 格式化

- 使用 `prettier` 自动格式化
- 行长度：100 字符
- 缩进：2 空格

## 命名

- 变量/函数：驼峰 `agentService`
- 类/接口：`PascalCase`
- 常量：`SCREAMING_SNAKE_CASE`
- 文件：`kebab-case`（`agent-service.ts`）

## 类型

- 必须显式标注接口/函数的返回类型
- 禁止使用 `any`，优先使用 `unknown` + 类型守卫
- 使用 `interface` 而非 `type` 定义对象结构（可扩展）

## 错误处理

- 使用 `throw` 抛错，不返回错误码
- 自定义错误类继承 `Error`
- async 函数使用 try/catch

## 导入

- 绝对路径：`@/controllers/agent`
- 相对路径：最多 3 层 `../../`

## 注释

- 使用 JSDoc 标注公共 API
- 单行注释 `//`（不用 `###`）
"""

    py_style = f"""# 代码风格

> 本文件定义 Python 代码风格约束。
> 自动生成于 {date_str}

---

## 格式化

- 使用 `black` 自动格式化
- 行长度：88 字符（black 默认）
- 缩进：4 空格

## 命名

- 变量/函数：`snake_case`
- 类：`PascalCase`
- 常量：`SCREAMING_SNAKE_CASE`
- 私有：`_single_leading_underscore`

## 类型标注

- 必须为公共函数添加类型标注
- 使用 `typing` 模块（`List`, `Dict`, `Optional`）
- 复杂类型使用 `TypeAlias`

## 错误处理

- 异常继承 `Exception` 或 `BaseException`
- 捕获具体异常类型，不用 `except Exception`
- 使用 `logging` 记录错误，不用 `print`

## 导入

- 分组：标准库 → 第三方 → 本地
- 禁止使用 `from module import *`
- 使用 `isort` 自动排序

## 文档

- 公共类/函数使用 docstring
- 格式：三引号
"""

    styles = {"go": go_style, "typescript": ts_style, "python": py_style}
    return styles.get(language, f"# 代码风格\n\n> 本文件定义 {language} 代码风格约束。\n> 自动生成于 {date_str}\n")


def generate_index_md(project_name: str, language: str, framework: str | None, structure: dict, layers: dict[str, str]) -> str:
    """生成 index.md 内容"""
    lang_name = LANG_DISPLAY.get(language, language.title())
    date_str = datetime.now().strftime("%Y-%m-%d")

    # 模块清单
    module_lines = []
    if layers:
        for layer_path, layer_name in sorted(layers.items()):
            parts = layer_path.split("/")
            module_name = parts[-1] if len(parts) > 1 else layer_path
            module_lines.append(f"| {layer_name} | `{layer_path}/` | |")
    else:
        top_dirs = sorted(set(d.split("/")[0] for d in structure.get("dirs", []) if d and "/" not in d and not d.startswith(".")))[:10]
        for d in top_dirs:
            module_lines.append(f"| {d} | `{d}/` | |")

    modules_md = "| 模块 | 位置 | 职责 |\n|------|------|------|\n" + "\n".join(module_lines) if module_lines else "| 模块 | 位置 | 职责 |\n|------|------|------|\n| （空项目） | — | — |"

    # 技术栈
    tech_rows = f"| 语言 | {lang_name} |\n| 框架 | {framework or '—'} |"

    # 目录树
    top_dirs = sorted(set(d.split("/")[0] for d in structure.get("dirs", []) if d and "/" not in d and not d.startswith(".")))[:15]
    dir_tree = "\n".join(f"├── {d}/" for d in top_dirs) if top_dirs else "└── （空项目）"

    # 关键文件（按语言默认）
    key_files_map = {
        "go": [("入口", "cmd/"), ("配置", "internal/config"), ("路由", "internal/handler"), ("业务", "internal/service"), ("数据", "internal/repository")],
        "typescript": [("入口", "src/index"), ("配置", "src/config"), ("路由", "src/routes"), ("业务", "src/services"), ("数据", "src/repositories")],
        "python": [("入口", "app/main.py"), ("配置", "app/config"), ("路由", "app/api"), ("业务", "app/services"), ("数据", "app/models")],
    }
    key_files = key_files_map.get(language, [("入口", "src/"), ("配置", "config/"), ("业务", "src/")])
    kf_lines = []
    for scene, pattern in key_files:
        matches = [f for f in structure.get("files", []) if pattern.split("/")[0] in f][:1]
        kf_lines.append(f"| {scene} | `{matches[0] if matches else pattern}` |")
    key_files_md = "| 场景 | 关键文件 |\n|------|---------|\n" + "\n".join(kf_lines) if kf_lines else "| 场景 | 关键文件 |\n|------|---------|"

    return f"""# {project_name} — 项目索引

> ⚠️ **维护规则**：每次新增/修改/删除文件后，必须同步更新本索引。
> 自动生成于 {date_str}

---

## 一、目录结构总览

```
{project_name}/
{dir_tree}
```

---

## 二、核心模块清单

{modules_md}

---

## 三、技术栈

{tech_rows}

---

## 四、关键文件导航

{key_files_md}

---

## 五、变更日志

> 变更日志独立在 `.aies/.ai/changelog.md`，避免每次加载 index 都带上历史 diff（省 token）。
"""


# ============================================================
# 填充逻辑
# ============================================================

def populate_specs(target: Path, project_name: str) -> list[str]:
    """填充所有 spec 文件（已有工程）"""
    actions = []

    language = detect_language(target) or "unknown"
    framework = detect_framework(target, language)
    structure = scan_directory_structure(target)
    layers = detect_layers(structure.get("dirs", []))
    top_dirs = sorted(set(d.split("/")[0] for d in structure.get("dirs", []) if d and "/" not in d and not d.startswith(".")))

    # 填充 architecture.md
    arch_path = target / ".aies" / "spec" / "architecture.md"
    if arch_path.exists():
        content = arch_path.read_text(encoding="utf-8")
        if "TODO" in content or "{{" in content:
            new_content = generate_architecture_md(language, framework, layers, top_dirs)
            arch_path.write_text(new_content, encoding="utf-8")
            actions.append(f"  FILL  {arch_path.relative_to(target)}")

    # 填充 code-style.md
    style_path = target / ".aies" / "spec" / "code-style.md"
    if style_path.exists():
        content = style_path.read_text(encoding="utf-8")
        if "TODO" in content or "{{" in content:
            new_content = generate_code_style_md(language)
            style_path.write_text(new_content, encoding="utf-8")
            actions.append(f"  FILL  {style_path.relative_to(target)}")

    # 填充 index.md
    index_path = target / ".aies" / ".ai" / "index.md"
    if index_path.exists():
        content = index_path.read_text(encoding="utf-8")
        if "{{PROJECT_NAME}}" in content or "TODO" in content:
            new_content = generate_index_md(project_name, language, framework, structure, layers)
            index_path.write_text(new_content, encoding="utf-8")
            actions.append(f"  FILL  {index_path.relative_to(target)}")

    return actions


def interactive_setup(target: Path, project_name: str) -> list[str]:
    """引导式设置（空工程）"""
    actions = []

    print("\n📋 引导式项目配置")
    print("=" * 50)

    # 语言选择
    lang_map = {"1": "go", "2": "typescript", "3": "python", "4": "java", "5": "rust", "6": "csharp"}
    lang_names = ["Go", "TypeScript", "Python", "Java", "Rust", "C#"]
    print("\n请选择项目语言：")
    for i, name in enumerate(lang_names, 1):
        print(f"  {i}. {name}")
    choice = input("选择 [1]: ").strip() or "1"
    language = lang_map.get(choice, "go")

    # 框架选择
    frameworks = {
        "go": ["Gin", "Echo", "Fiber", "Chi", "其他"],
        "typescript": ["NestJS", "Next.js", "Express", "Fastify", "其他"],
        "python": ["FastAPI", "Flask", "Django", "Chalice", "其他"],
        "java": ["Spring Boot", "Spring MVC", "其他"],
        "rust": ["Actix", "Rocket", "Axum", "其他"],
        "csharp": ["ASP.NET Core", "其他"],
    }
    fw_opts = frameworks.get(language, ["其他"])
    print(f"\n请选择{language}框架：")
    for i, fw in enumerate(fw_opts, 1):
        print(f"  {i}. {fw}")
    choice = input(f"选择 [1]: ").strip() or "1"
    idx = int(choice) - 1 if choice.isdigit() else 0
    framework = fw_opts[idx] if 0 <= idx < len(fw_opts) else fw_opts[0]

    # 项目类型
    print("\n项目类型：")
    print("  1. API 服务")
    print("  2. CLI 工具")
    print("  3. 前端应用")
    print("  4. 库/SDK")
    print("  5. 其他")
    choice = input("选择 [1]: ").strip() or "1"
    project_types = ["api", "cli", "frontend", "library", "other"]
    project_type = project_types[int(choice) - 1] if choice.isdigit() and 1 <= int(choice) <= 5 else "api"

    print("\n正在生成规范...")

    # 生成各文件
    layers = {
        "cmd/": "入口层（CLI）",
        "internal/domain/": "领域层",
        "internal/service/": "服务层",
        "internal/repository/": "仓储层",
        "api/": "入口层（API）",
    }
    structure = {"dirs": list(layers.keys()), "files": []}

    # 写入文件
    for path, content_fn in [
        (target / ".aies" / "spec" / "architecture.md", lambda: generate_architecture_md(language, framework, layers, list(layers.keys()))),
        (target / ".aies" / "spec" / "code-style.md", lambda: generate_code_style_md(language)),
        (target / ".aies" / ".ai" / "index.md", lambda: generate_index_md(project_name, language, framework, structure, layers)),
    ]:
        if path.exists():
            path.write_text(content_fn(), encoding="utf-8")
            actions.append(f"  FILL  {path.relative_to(target)}")

    return actions