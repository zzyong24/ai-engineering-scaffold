#!/usr/bin/env bash
# Pre-commit hook — 基础 AIES 规范检查
#
# 安装方式：
#   cp ci/pre-commit/ai-review-hook.sh .git/hooks/pre-commit
#   chmod +x .git/hooks/pre-commit

set -euo pipefail

EXIT_CODE=0
warn() { echo "::warning ::$*" >&2; }
fail() { echo "::error ::$*" >&2; EXIT_CODE=1; }

# 1. 代码文件变更则提醒索引更新
CODE_CHANGED=$(git diff --cached --name-only | grep -cE '\.(go|ts|tsx|js|jsx|py|java|rs)$' || true)
INDEX_CHANGED=$(git diff --cached --name-only | grep -cE '\.ai/index\.md|\.ai/changelog\.md' || true)
if [[ "$CODE_CHANGED" -gt 0 && "$INDEX_CHANGED" -eq 0 ]]; then
    warn "代码有变更但 .ai/index.md 未更新。如涉及结构变化请更新后再提交。"
fi

# 2. 检查是否有硬编码敏感信息
if git diff --cached | grep -iE "(password|secret|token)\s*=\s*['\"][^'\"]{8,}" >/dev/null; then
    fail "检测到可能的硬编码密钥/密码，请使用配置或环境变量"
fi

# 3. 检查是否有 console.log / fmt.Println 调试语句（Go/TS/JS）
if git diff --cached | grep -E '^\+.*(console\.log|fmt\.Println|debugger)\s*\(' >/dev/null; then
    warn "检测到调试输出语句（console.log / fmt.Println / debugger），确认是否应移除"
fi

# 4. 检查 commit message 是否标注 [ai-assisted]（如果是 AI 辅助的话）
# （可选，取决于团队约定）

exit $EXIT_CODE
