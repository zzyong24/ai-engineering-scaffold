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

    # 升级已有项目（diff 出模板变化，引导合并）
    python3 bootstrap.py --upgrade --target /path/to/project

模式：
    fresh   —— 全新项目，直接拷贝
    merge   —— 已有项目，保留已有文件
    add     —— 只添加缺失的文件，不覆盖任何已有文件
    upgrade —— 对比模板哈希，报告变更，引导合并
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sys
from datetime import datetime
from pathlib import Path

SCAFFOLD_DIR = Path(__file__).parent.resolve()
TEMPLATE_HASHES_FILE = ".aies/.template-hashes.json"

# Add scripts/lib to path for populate module
sys.path.insert(0, str(Path(__file__).parent / ".aies" / "scripts"))
from lib.populate import has_meaningful_code, populate_specs, interactive_setup  # noqa: E402, E501

# ============================================================
# 模板常量
# ============================================================

CORE_DIRS = [".aies"]

PLATFORM_MAP = {
    "claude": {
        "source": ".aies/platforms/claude",
        "targets": [
            ("CLAUDE.md", "CLAUDE.md"),  # 根目录，Claude Code 标准加载路径
            ("settings.json", ".aies/claude/settings.json"),
            ("hooks/", ".aies/claude/hooks/"),
            ("commands/", ".aies/claude/commands/"),
            ("agents/", ".aies/claude/agents/"),
        ],
    },
    "cursor": {
        "source": ".aies/platforms/cursor",
        "targets": [
            ("rules/", ".aies/cursor/rules/"),
            ("commands/", ".aies/cursor/commands/"),
        ],
    },
    "codebuddy": {
        "source": ".aies/platforms/codebuddy",
        "targets": [
            ("rules/", ".aies/codebuddy/rules/"),
        ],
    },
    "copilot": {
        "source": ".aies/platforms/copilot",
        "targets": [
            ("instructions/copilot-instructions.md", ".aies/copilot-instructions.md"),
        ],
    },
    "codex": {
        "source": ".aies/platforms/codex",
        "targets": [
            ("AGENTS.md", ".aies/AGENTS.md"),
        ],
    },
    "universal": {
        "source": ".aies/platforms/common",
        "targets": [
            ("AGENTS.md", ".aies/AGENTS.md"),
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
        # 跳过 __pycache__ 和 .pyc 文件
        if "__pycache__" in item.parts or item.suffix == ".pyc":
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
        ".aies/.template-hashes.json",
        ".aies/platforms/**/settings.json",
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


# ============================================================
# 模板哈希追踪
# ============================================================

def _file_md5(path: Path) -> str:
    """计算文件 MD5"""
    return hashlib.md5(path.read_bytes()).hexdigest()


def _collect_template_hashes() -> dict[str, str]:
    """收集 scaffold 所有模板文件的哈希"""
    hashes: dict[str, str] = {}
    for src_dir in [SCAFFOLD_DIR / ".aies"]:
        if not src_dir.is_dir():
            continue
        for f in src_dir.rglob("*"):
            if f.is_file():
                rel = str(f.relative_to(SCAFFOLD_DIR))
                hashes[rel] = _file_md5(f)
    for plat_cfg in PLATFORM_MAP.values():
        src = SCAFFOLD_DIR / plat_cfg["source"]
        for src_rel, _ in plat_cfg["targets"]:
            p = src / src_rel.rstrip("/")
            if p.is_file():
                rel = str(p.relative_to(SCAFFOLD_DIR))
                hashes[rel] = _file_md5(p)
            elif p.is_dir():
                for f in p.rglob("*"):
                    if f.is_file():
                        rel = str(f.relative_to(SCAFFOLD_DIR))
                        hashes[rel] = _file_md5(f)
    return hashes


def write_template_hashes(target: Path, dry_run: bool) -> str:
    """写入 .aies/.template-hashes.json"""
    hashes_path = target / TEMPLATE_HASHES_FILE
    hashes = _collect_template_hashes()
    meta = {
        "scaffold_version": datetime.now().strftime("%Y%m%d"),
        "generated_at": datetime.now().isoformat(),
        "files": hashes,
    }
    if not dry_run:
        hashes_path.parent.mkdir(parents=True, exist_ok=True)
        hashes_path.write_text(json.dumps(meta, indent=2, ensure_ascii=False), encoding="utf-8")
    return f"  WRITE  {TEMPLATE_HASHES_FILE}  ({len(hashes)} 个模板文件)"


def validate_installation(target: Path, required_files: list[str]) -> list[str]:
    """校验关键文件是否正确安装"""
    actions = []
    errors = []
    for f in required_files:
        path = target / f
        if path.exists():
            actions.append(f"  ✓ {f}")
        else:
            actions.append(f"  ✗ {f} — 缺失!")
            errors.append(f)
    if errors:
        actions.append(f"\n  ⚠️  {len(errors)} 个关键文件缺失，可能影响 AIES 正常运行")
        actions.append(f"  缺失文件: {', '.join(errors)}")
    return actions


def cmd_upgrade(target: Path, dry_run: bool) -> int:
    """升级模式：diff 出模板变化，引导合并"""
    hashes_path = target / TEMPLATE_HASHES_FILE
    if not hashes_path.is_file():
        print(f"❌ 未找到 {TEMPLATE_HASHES_FILE}，请先执行初始化（bootstrap.py --here）")
        return 1

    saved = json.loads(hashes_path.read_text(encoding="utf-8"))
    old_hashes: dict[str, str] = saved.get("files", {})
    old_version = saved.get("scaffold_version", "unknown")
    new_hashes = _collect_template_hashes()
    new_version = datetime.now().strftime("%Y%m%d")

    # diff
    added = [k for k in new_hashes if k not in old_hashes]
    removed = [k for k in old_hashes if k not in new_hashes]
    changed = [k for k in new_hashes if k in old_hashes and new_hashes[k] != old_hashes[k]]

    print(f"\n🔍 AIES 模板升级检查")
    print(f"   已安装版本: {old_version}")
    print(f"   当前版本:   {new_version}")
    print()

    if not added and not removed and not changed:
        print("✅ 模板无变化，项目已是最新版本。")
        return 0

    if added:
        print(f"📥 新增文件（{len(added)}）—— 可直接复制到项目：")
        for f in added:
            print(f"   + {f}")
        print()

    if changed:
        print(f"📝 模板已更新（{len(changed)}）—— 需要手动合并：")
        for f in changed:
            # 计算项目中对应目标文件的路径
            dst = _template_rel_to_target(f, target)
            project_modified = dst.is_file() and _file_md5(dst) != old_hashes.get(f, "")
            status = "⚠️  项目文件已被本地修改，需仔细合并" if project_modified else "✅ 项目文件未修改，可直接覆盖"
            print(f"   ~ {f}")
            print(f"       {status}")
        print()

    if removed:
        print(f"🗑️  已废弃文件（{len(removed)}）—— 建议检查并删除：")
        for f in removed:
            print(f"   - {f}")
        print()

    if not dry_run and (added or changed):
        answer = input("是否更新 .template-hashes.json 为新版本哈希？[y/N]: ").strip().lower()
        if answer == "y":
            meta = {
                "scaffold_version": new_version,
                "generated_at": datetime.now().isoformat(),
                "files": new_hashes,
            }
            hashes_path.write_text(json.dumps(meta, indent=2, ensure_ascii=False), encoding="utf-8")
            print("✅ 已更新 .template-hashes.json")

    print()
    print("手动合并步骤：")
    print("  1. 对照上面的变更列表，逐文件 diff scaffold/ 和项目中的文件")
    print("  2. 手动将模板新增内容合并进项目文件（保留你的自定义部分）")
    print("  3. 合并完成后再次运行 --upgrade 确认无变化")
    return 0


def _template_rel_to_target(template_rel: str, target: Path) -> Path:
    """将模板相对路径转换为项目目标路径（近似，不含平台映射）"""
    return target / template_rel


def post_process_placeholders(target: Path, project_name: str, dry_run: bool) -> list[str]:
    """替换模板占位符"""
    actions = []
    placeholders = {
        "{{PROJECT_NAME}}": project_name,
        "{{LAST_UPDATED}}": datetime.now().strftime("%Y-%m-%d"),
        "{{INIT_DATE}}": datetime.now().strftime("%Y-%m-%d"),
    }

    patterns = [".aies/**/*.md", "CLAUDE.md", ".aies/AGENTS.md"]

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
    p.add_argument("--upgrade", action="store_true", help="升级模式：检查模板变化并引导合并")
    p.add_argument("--dry-run", action="store_true", help="仅打印动作，不实际修改")
    return p.parse_args()


def main() -> int:
    args = parse_args()

    # ── 升级模式 ──────────────────────────────────────────────
    if args.upgrade:
        target = args.target
        if args.here or target is None:
            target = Path.cwd().resolve()
        if not target.is_dir():
            print(f"❌ 目标目录不存在: {target}", file=sys.stderr)
            return 1
        return cmd_upgrade(target, args.dry_run)

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

    # Step 0: 检测项目类型（在拷贝模板之前）
    all_actions.append("\n🔍 检测项目类型")
    project_has_code = has_meaningful_code(target)
    if project_has_code:
        all_actions.append("  检测到已有代码，将进入自动分析模式")
    else:
        all_actions.append("  检测到空工程，将进入引导式配置模式")

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

    # Step 5: 写入模板哈希（用于后续 --upgrade diff）
    all_actions.append("\n🔒 记录模板哈希（用于 --upgrade）")
    all_actions.append(write_template_hashes(target, dry_run))

    # Step 6: 智能填充（根据项目类型走不同分支）
    all_actions.append("\n🧠 智能填充规范文件")
    if project_has_code:
        all_actions.append("  自动分析已有代码，填充规范文件")
        all_actions.extend(populate_specs(target, cfg["project_name"]))
    else:
        all_actions.append("  引导式配置空工程规范")
        all_actions.extend(interactive_setup(target, cfg["project_name"]))

    # Step 7: 初始化开发者身份
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

    # Step 8: 初始化后校验
    if not dry_run:
        all_actions.append("\n🔍 初始化后校验")
        required_files = [
            "CLAUDE.md",
            ".aies/.ai/index.md",
            ".aies/spec/index.md",
            ".aies/workflow.md",
            ".aies/config.yaml",
        ]
        all_actions.extend(validate_installation(target, required_files))

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
        print("已自动填充规范文件：.aies/spec/architecture.md, .aies/spec/code-style.md, .aies/.ai/index.md")
        print()
        print("建议操作：")
        print("  1. 读 .aies/.ai/index.md 确认项目地图是否准确")
        print("  2. 读 .aies/spec/architecture.md 确认架构描述是否符合预期")
        print("  3. 如需调整，编辑对应文件（AIES 已根据项目代码自动生成了基础内容）")
        print()
        print("升级模板时：")
        print("  python3 bootstrap.py --upgrade --target <项目目录>")
    print("=" * 60)

    return 0


if __name__ == "__main__":
    sys.exit(main())
