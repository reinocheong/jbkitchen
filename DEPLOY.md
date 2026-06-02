# DEPLOY.md

> **开发信条：** 厨师简历栏 = 免费招聘栏位 → 吸引厨师注册 → 拿到线索 → KHL 销售谈供应。
> KHL 不介入安排厨师工作，不做中介。所有部署决策以此为准。

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

### 自动部署（cron）

系统使用 Hermes cron job `jbkitchen — auto publish` (ID: `5c97932548d0`)：

- **频率：** 8:00 / 10:00 / 12:00 / 14:00 / 16:00 / 18:00 / 20:00
- **脚本：** `~/.hermes/scripts/jbkitchen-auto-publish.sh` → 调用 `scripts/auto-publish.sh`
- **流程：** `aggregate.py`（刷新数据）→ `hugo --minify`（构建）→ `git push`（部署）
- **无变化时：** 自动跳过 commit（`|| true` 不中断）

### 手动部署（故障时）

```bash
cd ~/jbkitchen && bash scripts/auto-publish.sh    # 一键操作
```
或分步：
```bash
cd scripts && python3 aggregate.py   # 刷新数据
cd ../site && hugo --minify          # 构建
cd .. && git add -A && git commit -m "..." && git push  # 部署
```

### GitHub Actions 部署（备用，需新 token）
当前 token 缺少 `workflow` scope。如需 GitHub Actions：
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
| DOSM Open API | CPI 指数 + 通胀率 | ✅ 免费开放数据，无需 API key |
| exchangerate-api.com | MYR 实时汇率 | ✅ 免费，无需 API key |
| Google News RSS | 马来西亚餐饮新闻（22 关键词） | ✅ 免费 RSS，无需 API key |
| WhatsApp Baileys (wa_daemon3.js) | 冷冻鸡价实时抓取 | ⚠️ 需保持 daemon 运行（PID 174813） |

## Python 依赖

```bash
pip install requests feedparser
```

## 数据同步

Python 脚本自动双向同步：
- `data/*.json` → 原始数据（自动采集）
- `site/data/*.json` → Hugo 读取的数据

两个目录内容始终一致（`aggregate.py` 在写入时同步到两边）。

厨师数据（`site/data/chefs.json`）为手动维护，不与 `data/` 同步。

## 设置指南

见 `setup/SHEET_SETUP_GUIDE.md` — Google Sheet + Apps Script 部署步骤。
