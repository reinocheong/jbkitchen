#!/usr/bin/env bash
# jbkitchen — Auto publish pipeline
# 1. Refresh all data (news, prices, chicken prices, jobs, FB jobs)
# 2. Build Hugo site
# 3. Deploy to GitHub Pages
set -euo pipefail

PROJECT_DIR="/home/user/jbkitchen"
cd "$PROJECT_DIR"

# Step 1: Refresh data
python3 scripts/aggregate.py

# Step 1.5: Merge JobStreet extras if available (Windows Chrome CDP data)
if [ -f "/mnt/c/Users/User/Desktop/fb-cookie-extract/extra_jobs_output.json" ]; then
  echo "[auto-publish] Merging JobStreet extras..."
  python3 scripts/merge_extra_jobs.py
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
