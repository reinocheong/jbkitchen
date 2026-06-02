#!/usr/bin/env bash
# jbkitchen — Auto publish pipeline
# 1. Refresh all data (news, prices, chicken prices, jobs, FB jobs)
# 2. Build Hugo site
# 3. Deploy to GitHub Pages
set -euo pipefail

cd "$(dirname "$0")/.."

# Step 1: Refresh data
cd scripts
python3 aggregate.py

# Step 2: Build Hugo (preserve .nojekyll and CNAME)
cd ../site
hugo --minify
touch ../docs/.nojekyll

# Step 3: Deploy
cd ..
git add -A
git commit -m "auto: data refresh $(date +'%Y-%m-%d %H:%M')" || true
git push
