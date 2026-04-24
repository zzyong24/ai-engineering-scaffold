#!/usr/bin/env bash
# AIES 脚手架 Shell 版初始化脚本
# 当环境没有 Python 3 时使用（功能简化版，仅核心目录 + 通用平台入口）

set -euo pipefail

SCAFFOLD_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TARGET="${1:-$(pwd)}"
MODE="${2:-merge}"  # fresh | merge | add

echo "=============================================================="
echo "AIES Bootstrap (Shell 简化版)"
echo "=============================================================="
echo "目标: $TARGET"
echo "模式: $MODE"
echo "=============================================================="
echo ""
read -r -p "确认开始？[y/N]: " confirm
[[ "$confirm" != "y" ]] && { echo "已取消"; exit 0; }

copy_safe() {
    local src="$1"
    local dst="$2"
    if [[ -e "$dst" ]]; then
        if [[ "$MODE" == "fresh" ]]; then
            cp -r "$src" "$dst"
            echo "  OVERWRITE  $dst"
        else
            echo "  KEEP       $dst (已存在)"
        fi
    else
        mkdir -p "$(dirname "$dst")"
        cp -r "$src" "$dst"
        echo "  COPY       $dst"
    fi
}

echo ""
echo "📦 安装 .ai/"
for f in "$SCAFFOLD_DIR"/.ai/*.md "$SCAFFOLD_DIR"/.ai/*.md; do
    [[ -f "$f" ]] || continue
    copy_safe "$f" "$TARGET/.ai/$(basename "$f")"
done
if [[ -d "$SCAFFOLD_DIR/.ai/prompts" ]]; then
    for f in "$SCAFFOLD_DIR"/.ai/prompts/*.md; do
        [[ -f "$f" ]] || continue
        copy_safe "$f" "$TARGET/.ai/prompts/$(basename "$f")"
    done
fi

echo ""
echo "📦 安装 .aies/"
copy_safe "$SCAFFOLD_DIR/.aies/workflow.md" "$TARGET/.aies/workflow.md"
copy_safe "$SCAFFOLD_DIR/.aies/config.yaml" "$TARGET/.aies/config.yaml"
for f in "$SCAFFOLD_DIR"/.aies/spec/*.md; do
    [[ -f "$f" ]] || continue
    copy_safe "$f" "$TARGET/.aies/spec/$(basename "$f")"
done
mkdir -p "$TARGET/.aies/tasks" "$TARGET/.aies/workspace"
touch "$TARGET/.aies/tasks/.gitkeep" "$TARGET/.aies/workspace/.gitkeep"

echo ""
echo "🔌 安装通用平台入口"
copy_safe "$SCAFFOLD_DIR/platforms/common/AGENTS.md" "$TARGET/AGENTS.md"

echo ""
echo "📝 更新 .gitignore"
if [[ ! -f "$TARGET/.gitignore" ]] || ! grep -q "\.aies/\.developer" "$TARGET/.gitignore"; then
    {
        echo ""
        echo "# AIES"
        echo ".aies/.developer"
    } >> "$TARGET/.gitignore"
    echo "  已追加 .aies/.developer 到 .gitignore"
else
    echo "  .gitignore 已包含必要条目"
fi

echo ""
echo "=============================================================="
echo "✅ AIES Shell 版初始化完成"
echo ""
echo "注：Shell 版仅安装核心文件，未安装平台特定配置（Claude/Cursor 等）。"
echo "如需完整功能，请安装 Python 3 后运行："
echo "    python3 $SCAFFOLD_DIR/bootstrap.py --interactive"
echo "=============================================================="
