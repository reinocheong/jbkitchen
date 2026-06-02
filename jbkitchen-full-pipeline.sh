#!/usr/bin/env bash
# jbkitchen — Full pipeline: aggregate data → Hugo build → deploy
set -euo pipefail

PROJECT_DIR="/home/user/jbkitchen"
cd "$PROJECT_DIR"

echo "[auto-publish] 启动"
bash scripts/auto-publish.sh
