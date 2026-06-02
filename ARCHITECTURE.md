# ARCHITECTURE.md — 系统架构与工作流手册

> **开发信条：** 厨师简历栏 = 免费招聘栏位 → 吸引厨师注册 → 拿到线索 → KHL 销售谈供应。
> KHL 不介入安排厨师工作，不做中介。所有开发决策以此为准。

---

## 一、完整数据流（三路并行）

```mermaid
graph TD
    subgraph "① 定时刷新 (每天4次 8/12/16/20)"
        CRON[cron: 0 8,10,12,14,16,18,20 * * *] -->|auto-publish.sh| AG[aggregate.py]
        AG --> NF[news_fetcher.py<br/>Google News RSS ×22关键词]
        AG --> PT[price_tracker.py<br/>DOSM CPI + exchangerate-api]
        AG --> CP[chan_prices.py<br/>解析鸡价 /0.9 计算]
        NF --> NEWS[(site/data/news.json)]
        PT --> PRICES[(site/data/prices.json)]
    end

    subgraph "② 实时抓取 (WhatsApp Channel)"
        DAEMON[wa_daemon3.js<br/>PID 174813 :3456] -->|newsletterSubscribe| CHANNEL[鸡价频道<br/>120363405976277555@newsletter]
        DAEMON -->|messages.upsert| RAW[(data/chan_raw.json)]
        CP --> CHAN_PRICES[(site/data/chan_prices.json)]
    end

    subgraph "③ 构建部署 (auto-publish.sh)"
        SITE_DATA[(site/data/*.json)] -->|Hugo 读取| HUGO[hugo --minify]
        HUGO --> DOCS[(docs/ 静态站)]
        DOCS -->|git push| GH[GitHub Pages<br/>reinocheong.github.io/jbkitchen]
    end

    subgraph "展示层"
        GH --> HOME[首页 行业动态]
        HOME --> FX[汇率<br/>USD/CNY/SGD]
        HOME --> CPI[CPI 通胀<br/>DOSM 4类]
        HOME --> CHICKEN[鸡价表<br/>46项批发]
        HOME --> NEWS_FEED[新闻<br/>5条最新]
        HOME --> TOOLS[工具卡片<br/>4功能: 计算器/供应商/指南/招聘]
    end
```

## 二、每次操作什么时间点做什么

### 日常运行（自动）

| 时间 | 动作 | 触发 | 数据源 | 影响 |
|:---|:---|:---|:---|:---|
| 8:00 / 12:00 / 16:00 / 20:00 | `auto-publish.sh` 执行 | cron `5c97932548d0` | 新闻RSS + DOSM CPI + 汇率API + 鸡价原始消息 + 4大招聘网站 + FB招聘解析 | 网站自动更新 |
| 每日(不固定) | FB群组职位抓取 | cron `fb_job_scraper.js` | 8个FB厨房招聘群组 | 追加 `fb_jobs_raw.json`，下次cron自动解析上线 |
| 随时(通常周六下午) | 供营商在频道发新价目表 | `messages.upsert` 事件 | WhatsApp Channel | 覆盖 `chan_raw.json`，下次 cron (8/12/16/20点) 自动解析上线 |
| 每日(不固定) | DOSM 发布新月度 CPI | `price_tracker.py` 下次运行时 | DOSM API (cpi_headline) | 通胀数据月度更新 |

### 故障排查（人工）

> **第一步永远先跑 `./scripts/auto-publish.sh`** — 这步会刷新所有数据并部署，能解决90%的「数据不更新」问题。

**症状诊断表：**

| 症状 | 查什么 | 怎么修 |
|:---|:---|:---|
| 汇率/CPI 不动 | `cat site/data/prices.json \| jq .updated` | 手动跑 `python3 scripts/price_tracker.py` |
| 鸡价没更新 | `cat site/data/chan_raw.json \| jq .updated` | 检查 daemon 是否还活着 |
| 新闻没更新 | `cat site/data/news.json \| jq '.items \| length'` | 手动跑 `python3 scripts/news_fetcher.py` |
| 网站白屏/样式没了 | `curl -s https://reinocheong.github.io/jbkitchen/index.html \| head -5` | 检查 `.nojekyll` 文件是否存在、路径是否 `absURL`、?v3 版本号 |
| CSS 样式不对 | 查看浏览器 Console 的 404 错误 | 确认 CSS 链接加了 ?v3 版本号（GitHub Pages CDN 缓存） |
| 整个网站404 | `curl -sI https://reinocheong.github.io/jbkitchen/` | 检查 GitHub Pages 是否开启、docs/ 目录是否存在 |

### Daemon 相关操作

> **🚨 不要随意重启 daemon。** 频繁重启会触发 WhatsApp 封号（403/463错误）。

**daemon 状态检查：**
```bash
curl http://127.0.0.1:3456/health
# 期望: {"ok":true,"pid":174813,"connected":true,"uptime":"..."}
```

**daemon 日志：**
```bash
tail -50 /tmp/wa_daemon3.log
```

**daemon 必须重启（session 丢失/进程崩溃）时：**
```bash
# 1. 杀旧进程
pkill -f "node wa_daemon3.js"
sleep 2
# 2. 确认 session 文件还在
ls ~/leadpilot/wa/wa_session/creds.json && echo "session OK（无需扫码）" || echo "session 丢失，需要重新扫码"
# 3. 启动新 daemon
cd ~/leadpilot/wa && nohup node wa_daemon3.js > /tmp/wa_daemon3.log 2>&1 &
# 4. 等待连接
sleep 5
curl http://127.0.0.1:3456/health
```

**频道订阅确认（正常情况不需要重复执行，除非频道取消关注）：**
```bash
curl "http://127.0.0.1:3456/fetch_channel?invite=0029Vb6p7Qq5Ejy68g8VCj1U"
```

---

## 三、数据文件清单

| 文件 | 用途 | 更新方式 | 更新频率 |
|:---|:---|:---|:---|
| `site/data/prices.json` | 汇率 + CPI | `price_tracker.py` → `auto-publish.sh` | 每天4次 (cron 8/12/16/20) |
| `site/data/news.json` | 新闻列表 (30条) | `news_fetcher.py` → `auto-publish.sh` | 每天4次 (cron 8/12/16/20) |
| `site/data/chan_raw.json` | 鸡价原始消息 (daemon写入) | `wa_daemon3.js` `messages.upsert` | 供营商发新消息时 |
| `site/data/chan_prices.json` | 鸡价解析结果 (46项) | `chan_prices.py` → `auto-publish.sh` | 每天4次，只要有新原始数据 |
| `site/data/jobs.json` | JB餐饮招聘 (web聚合) | `scrape_jobs.py` → `auto-publish.sh` | 每天4次 (cron 8/12/16/20) |
| `data/fb_jobs_raw.json` | FB群组原始帖子 (append-only) | `fb_job_scraper.js` | 每天1次 |
| `data/fb_jobs_parsed.json` | FB职位解析结果 | `parse_fb_jobs.py` → `auto-publish.sh` | 每天4次 |
| `site/data/chefs.json` | 厨师样本数据 | 手动维护 | 按需 |
| `docs/` | 静态站输出 | `hugo --minify` → `auto-publish.sh` | 每天4次 + 手动 |

---

## 四、模块依赖关系

```
auto-publish.sh
  ├── aggregate.py
  │     ├── news_fetcher.py    → site/data/news.json
  │     ├── price_tracker.py   → site/data/prices.json
  │     ├── chan_prices.py     → site/data/chan_prices.json
  │     ├── scrape_jobs.py     → site/data/jobs.json + data/jobs.json
  │     └── parse_fb_jobs.py   → data/fb_jobs_parsed.json
  │
  ├── hugo --minify            → docs/ (读取 site/data/*.json)
  │
  └── git add + commit + push → GitHub Pages

fb_job_scraper.js (每天1次 cron)
  ├── Playwright → 8 个 FB 群组浏览
  └── 追加 data/fb_jobs_raw.json (append-only)

wa_daemon3.js (独立进程 PID 174813)
  └── messages.upsert          → site/data/chan_raw.json
```

## 五、鸡价解析规则

```
原始: (32) mid Joint Wing 12.50
  ↓ 解析
{item: "32", name: "Mid Joint Wing", price_src: 12.50}
  ↓ /0.9 计算
price_calc: 13.8889
  ↓ 四舍五入到 0.10
price: 13.90

名称清理规则:
- BB → Boneless Breast
- SBB → Skinless Boneless Breast  
- BL → Boneless Leg
- WL → Whole Leg
- *IM* → Import, *LO* → Local
- 品牌名保持大写 (CARGIL, TYSON)
- 尺寸范围 (0.8-0.9) 自动过滤（不是价格）
```

## 六、招聘数据流 (Job Scraping Pipeline)

```mermaid
graph TD
    subgraph "Web 抓取 (每天4次)"
        JORA[Jora: requests+BS4]
        HIREDLY[Hiredly: __NEXT_DATA__]
        MAUKERJA[Maukerja: Playwright (Nuxt.js)]
        MYFJ[MyFutureJobs: Playwright (Angular)]
        JORA --> SJ[scrape_jobs.py]
        HIREDLY --> SJ
        MAUKERJA --> SJ
        MYFJ --> SJ
        SJ --> JOBSJSON[(site/data/jobs.json)]
    end

    subgraph "FB 群组抓取 (每天1次)"
        FBSCRAPER[fb_job_scraper.js<br/>Playwright 8群组] --> RAW[(data/fb_jobs_raw.json<br/>APPEND ONLY)]
        RAW --> PARSE[parse_fb_jobs.py]
        PARSE --> FBJSON[(data/fb_jobs_parsed.json)]
    end

    subgraph "丰富化 (AI-searchable fields)"
        JOBSJSON --> ENRICH[_enrich_job: id/category/skills/location]
        FBJSON --> ENRICH
    end

    subgraph "Hugo 模板"
        JOBSJSON --> LIST[list.html]
        FBJSON -.-> LIST
        LIST --> DEPLOY[GitHub Pages]
    end
```

## 七、内容页面架构

```
site/content/
├── _index.md                    # 首页（汇率+CPI+新闻+鸡价+工具卡片）
├── chefs/
│   ├── _index.md                # 厨师简历列表
│   └── submit.md                # 厨师提交表单
├── suppliers/
│   ├── _index.md                # 供应商排行榜（15家）
│   └── khl-frozen-food.md       # KHL 详情页
├── calculator/
│   └── _index.md                # 成本计算器 V2
├── guides/
│   ├── _index.md                # 指南列表（卡片式）
│   ├── halal-cert.md            # 清真认证
│   ├── jb-license.md            # 餐饮执照
│   ├── frozen-food-guide.md     # 冷冻食材采购
│   ├── mesti-certification.md   # MeSTI 认证
│   ├── haccp-vs-iso-22000.md    # HACCP vs ISO 22000
│   ├── food-handling-certificate.md # 食品处理证书
│   ├── sst-service-tax-restaurant.md # SST 服务税
│   ├── start-frozen-food-business.md # 开冷冻食品生意
│   ├── cold-storage-temperature-standards.md # 冷库标准
│   ├── employee-epf-socso-eis-2025.md # EPF/SOCSO
│   └── frozen-food-import-permit-malaysia.md # 进口准证
├── about/
│   └── _index.md                # 关于 jbkitchen
├── contribute/
│   └── _index.md                # 行业投稿
└── dashboard/
    └── _index.md                # 流量统计面板
```

## 八、关键坑位

| 问题 | 原因 | 处理 |
|:---|:---|:---|
| websiteFetchMessages 超时 | Baileys 7.0.0-rc13 bug | 不走拉取，依赖 live `messages.upsert` |
| daemon 重启频繁 → 封号 | WhatsApp 检测频繁配对 | 分钟级指数退避，不重启 |
| 网站文件旧 | docs/ 没重新构建 | 手动跑 `auto-publish.sh` 或等 cron |
| cron 跑了但数据没变 | Python 脚本本身没出错但数据源无新内容 | 正常 — 数据源本身更新频率低于 cron |
| 鸡价显示缺项 | 供商家消息中无价格的商品（如"(1c) bb local "） | 自动跳过，只显示有价格的项 |
| CSS 嵌套 bug | `.source-badge {` 未闭合导致后续 848 行样式失效 | 确保每个 CSS class 正确闭合 |
| GitHub Pages CDN 缓存 | 更改 CSS/HTML 后浏览器看到旧版本 | 在 CSS 链接加 ?v3 版本号强制刷新 |
