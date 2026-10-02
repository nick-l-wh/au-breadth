#!/usr/bin/env bash
# Linux 每日更新：增量下載價格 → 計算廣度 → 52 週新高 → 有變更才 commit + push data/breadth.csv、highs_52w*.csv（與 universe.csv）。
# 股票池每 30 天自動更新一次（由 download_prices.py 的 ensure_universe 處理，與 JP 專案相同）。
# 用法：./run_daily.sh            （建議雪梨時間 17:00 之後，約香港 15:00；雪梨夏令時間期間約 14:00）
#       ./run_daily.sh --no-push  （只更新資料）
set -euo pipefail
cd "$(dirname "$(readlink -f "$0")")"

NO_PUSH=0
[[ "${1:-}" == "--no-push" ]] && NO_PUSH=1

PY=python3
[[ -x .venv/bin/python ]] && PY=.venv/bin/python

mkdir -p data
exec 9>data/.run_daily.lock
flock -n 9 || { echo "另一個 run_daily.sh 正在執行，略過"; exit 0; }

echo "== $(date '+%F %T %Z') / 雪梨 $(TZ=Australia/Sydney date '+%F %T %Z') =="

"$PY" scripts/download_prices.py </dev/null
"$PY" scripts/compute_breadth.py
"$PY" scripts/compute_highs.py

if (( NO_PUSH )); then echo "已略過推送（--no-push）"; exit 0; fi

git add data/breadth.csv data/universe.csv data/highs_52w.csv data/highs_52w_history.csv
if git diff --cached --quiet; then
  echo "資料沒有新的變更，不提交。"
  exit 0
fi
LAST=$(tail -n 1 data/breadth.csv | cut -d, -f1)
git commit -q -m "update breadth through ${LAST}"
git push -q origin HEAD:main
echo "已推送（資料至 ${LAST}），網頁約 1–2 分鐘後更新。"
