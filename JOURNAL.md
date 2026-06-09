# JOURNAL.md

> **开发信条：** 厨师简历栏 = 免费招聘栏位 → 吸引厨师注册 → 拿到线索 → KHL 销售谈供应。
> KHL 不介入安排厨师工作，不做中介。开发日志保持与此一致。

## 2026-06-02（续）

**操作人：AI**

### UI 重构 — 首页重排 + SVG 工具卡片 + 汉堡菜单 + 指南卡片

- 首页顺序从"汇率→鸡价→新闻"改为"汇率→CPI→新闻→鸡价"（用户确认）
- 工具卡片从纯文字改为 36px 彩色方块 + 白色 SVG 几何图案（计算器=网格，供应商=建筑，指南=书，招聘=人），无 emoji
- 手机端导航改为汉堡菜单（三条横线图标 → 点击展开全屏菜单 → X 关闭，带过渡动画）
- 指南列表页从蓝色链接改为卡片式布局（彩色渐变图标 + 标题 + 描述）
- 新增 About 页面（jbkitchen 定位为餐饮行业基础设施）
- 新增 Contribute 页面（邀请行业人士投稿，审核流程及署名政策）
- CSS 链接加 ?v3 版本号解决 GitHub Pages CDN 缓存问题

### CSS 核心 bug 修复

- `.source-badge {` 第 369 行未闭合括号 → 第 370-848 行全部被嵌套进 `.source-badge` 选择器，导致：
  - hero-btn 样式失效（紫色默认链接样式）
  - 职位列表样式丢失
  - 手机端 overflow-x 溢出水平滚动
- **修复**：闭合 369 行大括号，加上缺失的 hero-btn class 样式，加 `overflow-x: hidden` 手机端防护
- **教训**：CSS 大括号未闭合是最隐蔽的 bug——它不会报错，只是后续所有样式失效

### 8 篇新 SEO 指南（共 11 篇）

撰写并部署 8 篇结构化 SEO 指南，覆盖餐饮业高频搜索主题：

1. **MeSTI 认证** — KKM 食品安全认证完整流程，费用/时间/检查项目
2. **HACCP vs ISO 22000** — 对比型内容，适用场景与认证成本
3. **食品处理证书** — 每员工都要考，上课/考试/续期完整指南
4. **SST 服务税** — 年营业额门槛/注册/申报/罚款
5. **开冷冻食品批发生意** — 执照/供应商/冷库/客户开发
6. **冷库温度标准** — KKM 检查依据，不同食材的温度区间
7. **EPF SOCSO EIS 2025** — 最新缴交率表（雇主+员工）
8. **冷冻食品进口准证** — AP 申请流程/配额/港口检验

每篇含：结构化 H2/H3、FAQ（AI 搜索直接抽取）、具体数字、内部链接。

### 完整站点结构最终状态

```
首页（汇率 → CPI → 新闻 → 鸡价 + 4工具卡片）
├── /chefs/                 # 厨师简历列表（含分类标签+薪资格式化）
│   └── /chefs/submit/      # 免费挂简历（→ Google Form → WhatsApp + Sheet）
├── /suppliers/             # 15家供应商排行榜（KHL #1 金色）
│   └── /suppliers/khl-frozen-food/  # KHL 详情
├── /calculator/            # 成本计算器 V2
├── /guides/                # 11 篇 SEO 指南（卡片式入口）
├── /about/                 # 关于 jbkitchen
├── /contribute/            # 行业投稿
└── /dashboard/             # 流量面板
```

## 2026-06-02

**操作人：AI**

### 站点重构 — 移除广告 + 全站 emoji 清理 + 供应商表单
- 移除 advertise 页面（content/_index.md + layouts/list.html）
- 从导航栏、footer、dashboard 中移除所有广告引用
- 全站模板 emoji 清理：baseof.html, index.html, chefs/list.html, suppliers/list.html, suppliers/khl-frozen-food.html, dashboard/list.html, calculator/list.html, guides/list.html, guides/single.html
- emoji 替换方案：hero 按钮 icon 移除，工具卡片用单字替代，纯文字标题
- suppliers 页面：KHL 保持 #1 金色卡片，「推荐供应商」替代 ⭐；新增「商家提交」按钮 → Google Form
- 商家提交表单（Google Forms API）：商家名称、联系人、联系电话、地址、主要产品、备注
- hugo.toml：广告菜单项替换为流量面板
- 站点定位：100% 免费，无广告，无收费
- 设计语言：纯文字，无 emoji，保持专业干净
- 构建验证通过（hugo --minify）

### 招聘数据 AI 可搜索化 + SSOT 对齐
- 修改 scrape_jobs.py：新增 `_enrich_job` 函数，为每个职位添加 AI 可搜索字段
  - `id`：sha256 哈希（title+company+source）
  - `title_normalized`：标题规范化（ALL CAPS → Title Case）
  - `category`：分类（chef/cook/kitchen-crew/fb-service/management/other）
  - `employment_type`：雇佣类型检测（full-time/part-time/contract）
  - `location_normalized`：位置标准化（提取 JB 区域名如 Mount Austin）
  - `skills`：技能检测（Pastry/Baking/Chinese Cuisine 等 20+ 模式）
  - `description`：占位（后续可补充职位描述）
  - `salary.text_formatted`：人类可读薪资格式（RM3,000 - RM5,000/month）
- 更新 site/layouts/chefs/list.html：新增分类标签徽章、薪资格式化显示、图标装饰
- 新增 category-badge CSS 样式（6 种分类配色）
- 全量更新 7 个 SSOT 文档对齐当前项目状态

### 行业动态板块上线
- 重写 price_tracker.py：接入 DOSM Open API（cpi_headline + cpi_headline_inflation），获取官方 CPI 指数 + 通胀率数据
- 重写 news_fetcher.py：Google News RSS 22 个马来西亚餐饮关键词搜索，覆盖食材价格/政策法令/行业趋势/新山本地 4 大类
- 重写 aggregate.py：简化为直接调用 news_fetcher + price_tracker 双模块
- 修改首页模板：新增 CPI 通胀卡片（含 ▲/▼ 箭头 + 红绿颜色），汇率数值使用金色高亮，新闻列表显示来源/日期/分类标签
- 新增 CSS 样式：news-item, news-meta, news-category, live-card-wide
- 构建部署成功，git push 到 GitHub Pages
- 数据源：DOSM API（免费开放数据，最新 2026-04-01）、exchangerate-api.com（实时汇率）、Google News RSS（无 API key）

### 项目初始化
- 创建项目、Hugo 骨架、成本计算器、供应商目录、3 篇指南
- GitHub Pages 部署 + 自动化采集脚本（新闻+汇率）

### Reino 反馈 #1 — 需要 SSOT 协议
- 补全 7 文档，代码模块拆分（≤150 行），双日志

### Reino 反馈 #2 — 设计太毛坯，改人才平台
- 首页两条清晰路径（找厨师/找工作）
- 新增厨师简历模块（列表+详情+提交表单，6 样本数据）
- 厨师提交简历 → 推送到 KHL WhatsApp

### Reino 反馈 #3 — 加广告系统
- `/advertise/` 页面：4 个广告位，CPM 公式定价
- 公式：`浏览量 ÷ 1,000 × 位置系数 × RM 10`
- CountAPI 每页独立计数 + GA4 追踪（占位符）
- `/dashboard/` 实时显示所有页面浏览量 + 自动算出的广告价格

### Reino 反馈 #4 — 用 XLSX/Sheet 记录厨师
- 创建 setup/SHEET_SETUP_GUIDE.md（Google Sheet + Apps Script 部署指南）
- 明确厨师注册流程：表单 → WhatsApp + Google Sheet 双记录
- 更新 SSOT 文档对齐全部变更

### WhatsApp Channel 冷冻鸡价自动抓取上线
- 研究 DOSM API 找到 cpi_headline + cpi_headline_inflation 数据集（13 个 COICOP 分类），但 cpi_5d（5 位码细分类目）API 未开放
- 确认终极价格方案：DOSM CPI（自动）+ WhatsApp Channel 鸡价（实时）
- 识别到 Puchong Food Import & Export Sdn Bhd WhatsApp Channel（invite: 0029Vb6p7Qq5Ejy68g8VCj1U, JID: 120363405976277555@newsletter）
- 修改 wa_daemon3.js：添加 /fetch_channel HTTP 端点 + messages.upsert 监听器，捕获 channel 消息
- 重点注意：daemon 不再重启以免 WhatsApp 封号
- 创建 chan_prices.py：解析鸡价消息（46 项），压缩代码缩写（BB→Boneless Breast, SBB→Skinless Boneless Breast 等），执行 /0.9 计算并四舍五入到 0.10
- 首页模板：新增冷冻鸡价批发表（Item/Product/Price），全宽展示全部 46 项
- 更新 aggregate.py 加入 chan_prices 模块
- 数据源：WhatsApp Channel（邀请链接关注 + subscribeNewsletterUpdates 订阅）
- 已知限制：newsletterFetchMessages 在 Baileys 7.0.0-rc13 中超时，改用 live messages.upsert 监听

### SSOT 对齐审计
- 确认 cron job `5c97932548d0` 已启用，`0 8,12,16,20 * * *`（每天4次），与供营商周六下午更新节奏一致
- 修正 README.md / ARCHITECTURE.md 中「每2h」→「每天4次(8/12/16/20)」
- TODO.md 「设置 cron」已勾选完成
- 标记 7 个测试/废弃脚本为 DEPRECATED（check_commodities/check_prices/demo_cpi_data/list_dos_datasets/test_dosm_api/news_aggregator/news_filter）
- 网站 live HTTP 200，`.nojekyll` 存在，无旧协议副本，无僵尸 docs/ 引用

### 管道修复 + JobStreet 自动化 + SSOT 审计

**操作人：AI** — 2026-06-02 21:00

- 发现 cron 报错：`fb_job_scraper.js` 已被删除但 `~/.hermes/scripts/jbkitchen-full-pipeline.sh` 还在调用它
- 修复：更新 `~/.hermes/scripts/jbkitchen-full-pipeline.sh` 为最新版本（直接调 `auto-publish.sh`）
- 修复 `auto-publish.sh`：JobStreet 爬虫不再手动触发，加入管道自动执行（Windows Chrome 24/7 在线）
- `merge_extra_jobs.py` 已内置**去重合并**（title+company 复合键），不会覆盖已有数据
- 完整管道验证：53 内置 → 92 条（+39)，Hugo 30 页 → git push ✅
- SSOT 7 文档全部存在、相互引对齐
- `scripts/` 目录所有依赖脚本存在，无亡脚本引用
- 硬编码凭据搜索：无（0 命中）
- `docs/.nojekyll` 存在，`docs/` 目录干净（纯 Hugo 输出）
- 更新 jbkitchen skill 对齐管道变更

### 全管道验证 — 2026-06-03 17:05

**操作人：AI** — Chrome 重启后全管道测试

- aggregate.py: 53 条内置源 ✅
- JobStreet scraper: 117 raw → 44 kitchen-relevant ✅
- merge (dedup): 53 → 95 条（+42）✅
- Hugo 构建: 30 pages ✅
- GitHub Pages 部署 ✅

## 2026-06-09

**操作人：AI**

### 切换 JobStreet 爬虫从 Windows Chrome CDP 到 CloakBrowser

- 用户指出早上 6:00 cron 因 WiFi 问题失败（依赖 Windows Chrome CDP）
- 用户要求改用 CloakBrowser MCP 爬取 JobStreet
- 编写 `scripts/scrape_jobstreet_wsl.py`：使用 CloakBrowser 的 stealth Chromium (`/home/user/.cloakbrowser/chromium-146.0.7680.177.5/chrome`) 绕过 Cloudflare 反爬
- 验证：108 条 JobStreet 数据抓取成功，Cloudflare 完全绕过
- 更新 `merge_extra_jobs.py`：读取 WSL 路径取代 Windows 路径
- 更新 `auto-publish.sh`：调用 Python CloakBrowser 脚本取代 `cmd.exe` Windows Node.js
- 全管道验证：96 条招聘（+3 新），构建部署成功
- SSOT 7 文档全面对齐：README/TODO/ARCHITECTURE/DEPLOY 移除 WA daemon 引用、修正 cron 频率、加入 CloakBrowser 技术栈

### 供应商排行榜上线 + 计算器重做
- 使用 Windows Chrome CDP 通过 Google 搜索调研 JB 冷冻食品供应商，搜到实际结果
- 创建 `site/data/suppliers.json`（15家供应商，含名/描述/分类/网址/成立年份）
- 重写供应商排行榜页面：KHL 金色边框 #1 · 简洁卡片样式 · 品类标签 · 网站链接
- 清理所有「KHL=平台创办人」描述（footer Powered by / 介绍文案 / 无用 why 字段）
- 重写成本计算器：食材清单输入（6单位）→ 自动算成本率/毛利率/净利润 → 建议售价（40/45/50%目标）→ localStorage 保存 → 多菜对比表 → 保本分析
- 示例数据（咖喱鸡饭 RM10, 食材成本 RM4.44=44.4%）
- 鸡价表格 Item 改用顺序编号 1-46
- 全站底部导航增加供应商/计算器/广告/统计链接
