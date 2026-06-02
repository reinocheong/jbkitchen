# DEPLOY.md

## 当前部署

| 项目 | 值 |
|------|-----|
| 平台 | GitHub Pages |
| URL | https://reinocheong.github.io/jbkitchen/ |
| 源目录 | `/docs`（main 分支） |
| 正式域名 | 待购买（`jbkitchen.com`） |

## 部署流程

### 手动构建部署（当前方式）
```bash
cd site
hugo --minify    # 输出到 ../docs/
cd ..
git add -A && git commit -m "📦 构建更新" && git push
```

### 自动部署（暂不可用）
当前 GitHub token 缺少 `workflow` scope，无法 push workflow 文件。
`.github/workflows/` 目录已被移除（git rm），需要新 token 后才能恢复。

恢复步骤：
1. 生成带 `workflow` scope 的 GitHub personal access token
2. git checkout 回 workflow 文件（从 git history 找回）
3. 重新 push

## 外部依赖

| 服务 | 用途 | 状态 |
|------|------|------|
| CountAPI (countapi.xyz) | 每页面独立计数器 | ✅ 正常运行（免费版） |
| Google Analytics GA4 | 深度流量分析 | ⚠️ Measurement ID 为占位符，需替换 |
| Google Apps Script | 厨师注册表单→Google Sheet | ⚠️ 需要部署（见 setup/SHEET_SETUP_GUIDE.md） |
| Google Sheets | 厨师注册数据存档 | ⚠️ 需要创建（见 setup/SHEET_SETUP_GUIDE.md） |

## 数据同步

Python 脚本自动双向同步：
- `data/*.json` → 原始数据（自动采集）
- `site/data/*.json` → Hugo 读取的数据

两个目录内容始终一致（`aggregate.py` 在写入时同步到两边）。

厨师数据（`site/data/chefs.json`）为手动维护，不与 `data/` 同步。

## 设置指南

见 `setup/SHEET_SETUP_GUIDE.md` — Google Sheet + Apps Script 部署步骤。
