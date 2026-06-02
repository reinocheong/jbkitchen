# jbkitchen — 新山餐饮人才与经营平台

> 厨师找工作 · 老板找人才 · 餐厅找供应商 → KHL Frozen Food

## 一句话定位

新山餐饮双面市场平台：厨师挂简历找工作，餐厅老板找人才+找供应商+算成本，自然引导到 KHL。站点 100% 免费，无广告。

## 商业模式

```
免费平台：
  ① 厨师免费挂简历 → 餐厅老板自己联系厨师（KHL 不介入）
  ② KHL 销售拿到厨师资料 → 联系谈食材供应合作
  ③ 供应商目录（KHL 置顶 #1） + 成本计算器 + 指南 → 吸引餐厅老板
  ④ 供应商可通过表单自行提交加入排行（免费收录）
```

**用这个公式理解：** 厨师简历栏 = 招聘栏位 ⟶ 吸引厨师注册 ⟶ 拿到线索 ⟶ KHL 销售谈供应

## 技术栈

| 层 | 技术 |
|---|------|
| 生成器 | Hugo v0.145 (extended) |
| 数据采集 | Python 3.11 (requests + BeautifulSoup + Playwright), Node.js + Playwright (FB groups) |
| 数据源（行业） | DOSM Open API（CPI）, exchangerate-api.com（汇率）, Google News RSS（新闻）, WhatsApp Channel（冷冻鸡批发价） |
| 数据源（招聘） | Jora, Hiredly, Maukerja, MyFutureJobs（JB 餐饮招聘）+ Facebook groups |
| 部署 | GitHub Pages（`/docs` 目录，main 分支） |
| 自动化 | 手动构建推送（token 缺少 workflow scope） |
| 计数 | CountAPI（免费云端计数） |
| 表单 | Google Apps Script → Google Sheets（厨师注册） |
| 域名 | 当前 `reinocheong.github.io/jbkitchen`，正式期 `jbkitchen.com` |

## 项目目录

```
jbkitchen/
├── site/             # Hugo 源码
│   ├── content/      # Markdown 页面
│   ├── layouts/      # Go HTML 模板
│   ├── static/       # CSS
│   ├── data/         # Hugo 读取的 JSON（含自动+手动数据）
│   └── hugo.toml     # Hugo 配置
├── scripts/          # Python 自动化（新闻/汇率/鸡价/招聘采集）
│   ├── aggregate.py        # 主调度器（自动调用所有子模块）
│   ├── news_fetcher.py     # Google News RSS ×22关键词
│   ├── price_tracker.py    # DOSM CPI + 汇率
│   ├── chan_prices.py      # WhatsApp Channel 鸡价解析 /0.9
│   ├── scrape_jobs.py      # JB 餐饮招聘聚合（Jora/Hiredly/Maukerja/MyFutureJobs）
│   ├── parse_fb_jobs.py    # Facebook 群组招聘帖子解析
│   ├── fb_job_scraper.js   # Facebook 群组职位帖子抓取
│   └── auto-publish.sh     # cron 包装脚本（数据→构建→部署）
├── data/             # 原始 JSON
├── docs/             # 构建输出 → GitHub Pages
├── setup/            # 部署/集成指南（如 GAS Sheet 设置）
├── README.md         # ← 你现在在这
├── ARCHITECTURE.md   # 系统拓扑
├── DEPLOY.md         # 部署流程
├── TODO.md           # 开发状态
├── JOURNAL.md        # 开发日志
├── MEMORY.md         # 踩坑记录
└── USER.md           # 用户画像
```

## 核心页面

| 页面 | 功能 | 目标用户 |
|------|------|---------|
| `/` | 首页：行业动态(汇率/CPI/鸡价/新闻) | 所有人 |
| `/chefs/` | 厨师简历列表+详情 | 餐厅老板 |
| `/chefs/submit/` | 厨师免费挂简历（→WhatsApp→Sheet） | 厨师 |
| `/suppliers/` | 供应商排行榜（15家，KHL #1 + 商家提交入口） | 餐厅老板 |
| `/suppliers/khl-frozen-food/` | KHL 详情+询价表单 | 潜在客户 |
| `/calculator/` | 菜品成本计算器 V2（成本卡+多菜对比+保本分析） | 准备/已开餐厅 |
| `/guides/` | 经营指南（清真认证/执照/采购） | 准备开餐厅 |
| `/dashboard/` | 流量统计面板 | jbkitchen 运营 |

## 关键约定

- 单脚本 ≤150 行
- 新闻 RSS 源必须经过餐饮关键词过滤
- KHL 在所有供应商列表排第一位，带「推荐供应商」标签
- 所有指南底部有 KHL CTA
- 站点 100% 免费 — 无广告，无收费（已移除广告页面和 CPM 定价）
- 厨师注册数据流向：网站表单 → WhatsApp 通知 → Google Sheet 记录
- **设计语言：纯文字，无 emoji** — 保持专业干净的外观

## 系统工作流

> 详细架构图和数据流见 `ARCHITECTURE.md`

```
┌─ ① cron (每天 8/12/16/20 点) ──────────────┐
│  auto-publish.sh                             │
│    ├─ python3 aggregate.py                   │
│    │    ├─ news_fetcher.py    → news.json     │
│    │    ├─ price_tracker.py   → prices.json   │
│    │    ├─ chan_prices.py     → chan_prices.json│
│    │    ├─ scrape_jobs.py     → jobs.json      │
│    │    └─ parse_fb_jobs.py   → fb_jobs_parsed.json│
│    ├─ hugo --minify          → docs/          │
│    └─ git push               → GitHub Pages   │
└──────────────────────────────────────────────┘

┌─ ② Facebook 群组抓取 (每天 1 次) ─────────────┐
│  fb_job_scraper.js                            │
│    ├─ Playwright → 8 个 FB 群组浏览            │
│    ├─ 关键词过滤 → fb_jobs_raw.json (append)   │
│    └─ 下次 auto-publish.sh 自动解析上线         │
└──────────────────────────────────────────────┘
```
┌─ ③ WhatsApp Channel (实时) ──────────────────┐
│  供营商发价 → wa_daemon3.js (PID 174813)     │
│    → messages.upsert → chan_raw.json         │
│    → 下次 cron 自动解析上线                    │
└──────────────────────────────────────────────┘
```

**数据更新来源：**
| 数据 | 来源 | 频率 |
|:---|:---|:---|
| 💱 汇率 | exchangerate-api.com | 每天4次 (cron 8/12/16/20) |
| 📊 CPI 通胀 | DOSM Open API (cpi_headline) | 每天4次 / 每月更新 |
| 🐓 鸡价 | WhatsApp Channel (120363405976277555@newsletter) | 供营商(通常周六下午)发消息 + cron 解析 |
| 📰 新闻 | Google News RSS ×22关键词 | 每天4次 (cron 8/12/16/20) |
