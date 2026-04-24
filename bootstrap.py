#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AIES 脚手架一键初始化脚本

用法：
    # 交互式（推荐）
    python3 bootstrap.py --interactive

    # 指定参数
    python3 bootstrap.py --target /path/to/project --developer your-name \\
        --platforms claude,cursor,codebuddy --language go --mode merge

    # 最简（当前目录，所有平台，合并模式）
    python3 bootstrap.py --here --developer your-name

模式：
    fresh   —— 全新项目，直接拷贝
    merge   —— 已有项目，保留已有文件
    add     —— 只添加缺失的文件，不覆盖任何已有文件
"""

from __future__ import annotations

import argparse
import shutil
import sys
from datetime import datetime
from pathlib import Path

SCAFFOLD_DIR = Path(__file__).parent.resolve()

# ============================================================
# 模板常量
# ============================================================

CORE_DIRS = [".ai", ".aies"]

PLATFORM_MAP = {
    "claude": {
        "source": "platforms/claude",
        "targets": [
            ("CLAUDE.md", "CLAUDE.md"),
            ("settings.json", ".claude/settings.json"),
            ("hooks/", ".claude/hooks/"),
            ("commands/", ".claude/commands/"),
            ("agents/", ".claude/agents/"),
        ],
    },
    "cursor": {
        "source": "platforms/cursor",
        "targets": [
            ("rules/", ".cursor/rules/"),
            ("commands/", ".cursor/commands/"),
        ],
    },
    "codebuddy": {
        "source": "platforms/codebuddy",
        "targets": [
            ("rules/", ".codebuddy/rules/"),
        ],
    },
    "copilot": {
        "source": "platforms/copilot",
        "targets": [
            ("instructions/copilot-instructions.md", ".github/copilot-instructions.md"),
        ],
    },
    "codex": {
        "source": "platforms/codex",
        "targets": [
            ("AGENTS.md", "AGENTS.md"),
        ],
    },
    "universal": {
        "source": "platforms/common",
        "targets": [
            ("AGENTS.md", "AGENTS.md"),
        ],
    },
}

ALL_PLATFORMS = list(PLATFORM_MAP.keys())


# ============================================================
# 拷贝逻辑
# ============================================================

def copy_file(src: Path, dst: Path, mode: str, dry_run: bool) -> str:
    """拷贝单个文件。返回动作描述。"""
    if dst.exists():
        if mode == "add":
            return f"  SKIP (已存在)  {dst}"
        if mode == "merge":
            # merge 模式下也不覆盖现有文件，交由用户手动合并
            return f"  KEEP (已存在)  {dst}"
    if not dry_run:
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
    return f"  COPY           {dst}"


def copy_tree(src: Path, dst: Path, mode: str, dry_run: bool) -> list[str]:
    actions = []
    for item in src.rglob("*"):
        if item.is_dir():
            continue
        rel = item.relative_to(src)
        target = dst / rel
        actions.append(copy_file(item, target, mode, dry_run))
    return actions


def install_core(target: Path, mode: str, dry_run: bool) -> list[str]:
    actions = []
    for d in CORE_DIRS:
        src = SCAFFOLD_DIR / d
        dst = target / d
        if not src.is_dir():
            continue
        actions.append(f"\n📦 安装核心目录: {d}/")
        actions.extend(copy_tree(src, dst, mode, dry_run))
    return actions


def install_platform(
    platform: str, target: Path, mode: str, dry_run: bool
) -> list[str]:
    actions = [f"\n🔌 安装平台适配: {platform}"]
    cfg = PLATFORM_MAP[platform]
    source = SCAFFOLD_DIR / cfg["source"]
    for src_rel, dst_rel in cfg["targets"]:
        src = source / src_rel.rstrip("/")
        dst = target / dst_rel.rstrip("/")
        if not src.exists():
            actions.append(f"  SKIP (源不存在)  {src}")
            continue
        if src.is_file():
            actions.append(copy_file(src, dst, mode, dry_run))
        else:
            actions.extend(copy_tree(src, dst, mode, dry_run))
    return actions


def write_gitignore_lines(target: Path, dry_run: bool) -> str:
    """确保 .gitignore 包含必要行"""
    gi_path = target / ".gitignore"
    required = [
        ".aies/.developer",
    ]

    existing = gi_path.read_text(encoding="utf-8") if gi_path.is_file() else ""
    missing = [line for line in required if line not in existing]
    if not missing:
        return "  .gitignore 已包含必要条目"

    if dry_run:
        return f"  .gitignore 将追加: {', '.join(missing)}"

    with gi_path.open("a", encoding="utf-8") as f:
        if existing and not existing.endswith("\n"):
            f.write("\n")
        f.write("\n# AIES\n")
        for line in missing:
            f.write(line + "\n")
    return f"  .gitignore 已追加: {', '.join(missing)}"


def post_process_placeholders(target: Path, project_name: str, dry_run: bool) -> list[str]:
    """替换模板占位符"""
    actions = []
    placeholders = {
        "{{PROJECT_NAME}}": project_name,
        "{{LAST_UPDATED}}": datetime.now().strftime("%Y-%m-%d"),
        "{{INIT_DATE}}": datetime.now().strftime("%Y-%m-%d"),
    }

    patterns = [".ai/*.md", ".aies/**/*.md", "CLAUDE.md", "AGENTS.md"]

    for pat in patterns:
        for f in target.glob(pat):
            if not f.is_file():
                continue
            content = f.read_text(encoding="utf-8")
            new_content = content
            for k, v in placeholders.items():
                new_content = new_content.replace(k, v)
            if new_content != content:
                if not dry_run:
                    f.write_text(new_content, encoding="utf-8")
                actions.append(f"  EDIT  {f.relative_to(target)}")
    return actions


# ============================================================
# 交互式
# ============================================================

def interactive_config() -> dict:
    print("=" * 60)
    print("AIES — AI Engineering Scaffold 交互式初始化")
    print("=" * 60)
    print()

    default_target = Path.cwd().resolve()
    target = input(f"目标项目目录 [{default_target}]: ").strip()
    target = Path(target) if target else default_target

    dev = input("开发者名称（用于会话日志，留空跳过初始化）: ").strip()

    print()
    print("可选平台：")
    for i, p in enumerate(ALL_PLATFORMS, 1):
        print(f"  {i}. {p}")
    print("  0. 全部")
    print()
    choice = input("启用哪些平台？（逗号分隔编号 / 0=全部）[0]: ").strip() or "0"
    if choice == "0":
        platforms = ALL_PLATFORMS
    else:
        idxs = [int(x.strip()) - 1 for x in choice.split(",") if x.strip()]
        platforms = [ALL_PLATFORMS[i] for i in idxs if 0 <= i < len(ALL_PLATFORMS)]

    print()
    print("初始化模式：")
    print("  1. fresh  —— 全新项目（目标目录为空，或允许覆盖）")
    print("  2. merge  —— 合并（已有文件保留，新增文件写入）[推荐]")
    print("  3. add    —— 仅添加缺失文件")
    mode_choice = input("模式 [2]: ").strip() or "2"
    mode = {"1": "fresh", "2": "merge", "3": "add"}.get(mode_choice, "merge")

    print()
    project_name = input(f"项目名称 [{target.name}]: ").strip() or target.name

    return {
        "target": target,
        "developer": dev,
        "platforms": platforms,
        "mode": mode,
        "project_name": project_name,
        "dry_run": False,
    }


# ============================================================
# 主流程
# ============================================================

def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="AIES 脚手架初始化")
    p.add_argument("--interactive", "-i", action="store_true", help="交互式配置")
    p.add_argument("--target", type=Path, default=None, help="目标目录")
    p.add_argument("--here", action="store_true", help="目标为当前目录")
    p.add_argument("--developer", default="", help="开发者名称")
    p.add_argument("--project-name", default="", help="项目名称（用于填充模板）")
    p.add_argument(
        "--platforms", default="claude,cursor,codebuddy,universal",
        help=f"启用平台（逗号分隔）。可选: {','.join(ALL_PLATFORMS)}; 传 all 表示全部",
    )
    p.add_argument(
        "--mode", choices=["fresh", "merge", "add"], default="merge",
        help="安装模式（默认 merge）",
    )
    p.add_argument("--dry-run", action="store_true", help="仅打印动作，不实际修改")
    return p.parse_args()


def main() -> int:
    args = parse_args()

    if args.interactive:
        cfg = interactive_config()
    else:
        target = args.target
        if args.here or target is None:
            target = Path.cwd().resolve()
        platforms_raw = args.platforms.strip().lower()
        if platforms_raw == "all":
            platforms = ALL_PLATFORMS
        else:
            platforms = [p.strip() for p in platforms_raw.split(",") if p.strip()]
            invalid = [p for p in platforms if p not in ALL_PLATFORMS]
            if invalid:
                print(f"❌ 未知平台: {invalid}", file=sys.stderr)
                print(f"   可选: {ALL_PLATFORMS}", file=sys.stderr)
                return 1
        cfg = {
            "target": target,
            "developer": args.developer,
            "platforms": platforms,
            "mode": args.mode,
            "project_name": args.project_name or target.name,
            "dry_run": args.dry_run,
        }

    target: Path = cfg["target"]
    mode: str = cfg["mode"]
    dry_run: bool = cfg["dry_run"]

    if not target.is_dir():
        print(f"❌ 目标目录不存在: {target}", file=sys.stderr)
        return 1

    print()
    print("=" * 60)
    print(f"目标目录:   {target}")
    print(f"项目名称:   {cfg['project_name']}")
    print(f"模式:       {mode}")
    print(f"平台:       {', '.join(cfg['platforms'])}")
    print(f"开发者:     {cfg['developer'] or '(跳过)'}")
    print(f"Dry Run:    {dry_run}")
    print("=" * 60)

    if not dry_run:
        confirm = input("\n确认开始初始化？[y/N]: ").strip().lower()
        if confirm != "y":
            print("已取消。")
            return 0

    all_actions: list[str] = []

    # Step 1: 核心目录
    all_actions.extend(install_core(target, mode, dry_run))

    # Step 2: 平台适配
    for plat in cfg["platforms"]:
        all_actions.extend(install_platform(plat, target, mode, dry_run))

    # Step 3: .gitignore
    all_actions.append("\n📝 更新 .gitignore")
    all_actions.append(write_gitignore_lines(target, dry_run))

    # Step 4: 占位符替换
    all_actions.append("\n✏️ 替换占位符")
    all_actions.extend(post_process_placeholders(target, cfg["project_name"], dry_run))

    # Step 5: 初始化开发者身份
    if cfg["developer"] and not dry_run:
        import subprocess
        script = target / ".aies" / "scripts" / "init-developer.py"
        if script.is_file():
            all_actions.append("\n👤 初始化开发者身份")
            try:
                subprocess.run(
                    [sys.executable, str(script), cfg["developer"]],
                    cwd=target, check=False,
                    input="y\n", text=True,
                )
            except Exception as e:
                all_actions.append(f"  (失败：{e})")

    # 输出
    print()
    for a in all_actions:
        print(a)

    print()
    print("=" * 60)
    if dry_run:
        print("✅ Dry Run 完成（未实际修改文件）")
    else:
        print("✅ AIES 初始化完成！")
        print()
        print("下一步：")
        print("  1. 读 docs/philosophy.md 了解方法论")
        print("  2. 读 .aies/workflow.md 了解工作流")
        print("  3. 编辑 .ai/index.md 填写项目地图")
        print("  4. 编辑 .aies/spec/architecture.md 填写架构约束")
        print("  5. 运行 python3 .aies/scripts/session.py get-context 测试")
    print("=" * 60)

    return 0


if __name__ == "__main__":
    sys.exit(main())
