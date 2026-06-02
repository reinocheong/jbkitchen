#!/usr/bin/env bash
# jbkitchen — FB job scraper + aggregate pipeline
# Runs: FB scraper → parse FB → aggregate (Jora/Hiredly/Maukerja/MyFutureJobs) → Hugo build → deploy
set -euo pipefail

cd "$(dirname "$0")/.."

# Step 1: FB job scraper (Playwright, ~2-3 min)
echo "[fb_job_scraper] 启动"
timeout 120 node scripts/fb_job_scraper.js || echo "[fb_job_scraper] ⚠️ 部分失败"

# Step 2-4: Aggregate (includes parse_fb + web scrapers + Hugo build + deploy)
echo "[auto-publish] 启动"
bash scripts/auto-publish.sh
