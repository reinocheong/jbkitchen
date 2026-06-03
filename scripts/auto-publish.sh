#!/usr/bin/env bash
# jbkitchen — Auto publish pipeline
# 1. Refresh all data (news, prices, chicken prices, jobs, FB jobs)
# 2. Build Hugo site
# 3. Deploy to GitHub Pages
# auto-publish.sh — 完整数据管道 + JobStreet (Chrome CDP) + Hugo → GitHub Pages
# timeout: 该脚本自身约3分钟，cron 默认180s足够
set -euo pipefail

PROJECT_DIR="/home/user/jbkitchen"
PYTHON="$PROJECT_DIR/venv/bin/python3"
cd "$PROJECT_DIR"

# Step 1: Refresh data (Jora, Hiredly, Maukerja, MyFutureJobs)
$PYTHON scripts/aggregate.py

# Step 1.5: Scrape JobStreet via Windows Chrome + merge (dedup by title+company)
echo "[auto-publish] Scraping JobStreet via Windows Chrome..."
if cmd.exe /c "cd /d C:\Users\User\Desktop\fb-cookie-extract && node scrape_extra_jobs.js" 2>/dev/null; then
  echo "[auto-publish] Merging JobStreet extras (dedup)..."
  $PYTHON scripts/merge_extra_jobs.py
else
  echo "[auto-publish] ⚠️ JobStreet scraper failed (Chrome offline?), continuing with built-in sources only"
fi

# Step 2: Build Hugo (preserve .nojekyll and CNAME)
cd site
hugo --minify
touch ../docs/.nojekyll

# Step 3: Deploy
cd "$PROJECT_DIR"
git add -A
git commit -m "auto: data refresh $(date +'%Y-%m-%d %H:%M')" || true
git push
