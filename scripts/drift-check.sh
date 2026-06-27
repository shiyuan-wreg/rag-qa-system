#!/usr/bin/env bash
# drift-check —— 开局(`继续 X`)快速核对:文档是否落后于代码。
# 目标:用一次调用拿到"事实源(git)快照 + 文档声称的日期",取代手动重建状态的十几次命令。
# 输出尽量短,只在疑似漂移处加 ⚠。局限:同一天合并/新增的内容靠日期查不出(仍需人工眼看 commit 列表)。
# 用法:bash scripts/drift-check.sh
set -uo pipefail
cd "$(git rev-parse --show-toplevel 2>/dev/null)" || { echo "不在 git 仓库"; exit 1; }

LATEST_DATE=$(git log -1 --format=%cd --date=short)
BR=$(git branch --show-current)
echo "== git 事实源 =="
echo "HEAD     : $(git log -1 --format='%h %cd %s' --date=short)"
echo "branch   : ${BR:-(detached)}"
if git rev-parse --verify -q "origin/$BR" >/dev/null; then
  echo "vs origin: $(git rev-list --left-right --count "origin/$BR...$BR" | awk '{print "behind "$1" / ahead "$2}')"
fi
DIRTY=$(git status -s | wc -l | tr -d ' ')
[ "$DIRTY" -gt 0 ] && echo "⚠ 未提交改动: $DIRTY 个文件(git status -s 看)"

# 自上次"文档日期"以来的提交,供人工核对覆盖(同一天盲区靠这个补)
echo "== 文档 vs 代码 =="
chk() { # $1=标签 $2=文档里抓到的日期
  local label="$1" d="$2"
  if [ -z "$d" ]; then echo "$label: 未找到日期"; return; fi
  if [[ "$d" < "$LATEST_DATE" ]]; then echo "⚠ $label 最新=$d,落后于最新提交($LATEST_DATE) → 可能漏记"
  else echo "$label 最新=$d(不早于最新提交,OK 但仍需眼看同日内容)"; fi
}

PS=docs/PROJECT-STATE.md
[ -f "$PS" ] && chk "PROJECT-STATE" "$(grep -oE '[0-9]{4}-[0-9]{2}-[0-9]{2}' "$PS" | head -1)"

CL=frontends/portfolio/src/data/changelogs.ts
[ -f "$CL" ] && chk "CHANGELOG" "$(grep -oE "date: '[0-9-]{10}'" "$CL" | head -1 | grep -oE '[0-9]{4}-[0-9]{2}-[0-9]{2}')"

echo "dev-log  : 非仓库文件,用 MCP get_project_status(ai-demos)核对最新日期"

# 列出最近若干提交主题,人工对照上面文档是否都覆盖到
echo "== 最近 12 条提交(核对文档/changelog/dev-log 是否覆盖)=="
git log -12 --format='  %cd %s' --date=short
