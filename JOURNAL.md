# JOURNAL.md

> **开发信条：** 厨师简历栏 = 免费招聘栏位 → 吸引厨师注册 → 拿到线索 → KHL 销售谈供应。
> KHL 不介入安排厨师工作，不做中介。开发日志保持与此一致。

## 2026-06-02

**操作人：AI**

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
- 修改 parse_fb_jobs.py：导入 `_enrich_job` 为 FB 职位添加相同字段
- 更新 site/layouts/chefs/list.html：新增分类标签徽章、薪资格式化显示、图标装饰
- 新增 category-badge CSS 样式（6 种分类配色 + source-facebook）
- 全量更新 7 个 SSOT 文档对齐当前项目状态
  - README.md：目录树、数据源表、cron 流程（新增招聘采集+FB抓取）
  - ARCHITECTURE.md：新增「招聘数据流」Mermaid 图、数据文件清单、模块依赖
  - DEPLOY.md：Python 依赖（playwright/beautifulsoup4）、FB scraper cron
  - TODO.md：标记本会话 4 项完成
  - JOURNAL.md：追加本条目
  - MEMORY.md：新增招聘采集/FB抓取坑位
  - USER.md：补充 Reino/设计语言/商业模式关键点

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
- **操作人：AI | 2026-06-02 下午**
- 研究 DOSM API 找到 cpi_headline + cpi_headline_inflation 数据集（13 个 COICOP 分类），但 cpi_5d（5 位码细分类目）API 未开放
- 确认终极价格方案：DOSM CPI（自动）+ WhatsApp Channel 鸡价（实时）
- 识别到 Puchong Food Import & Export Sdn Bhd WhatsApp Channel（invite: 0029Vb6p7Qq5Ejy68g8VCj1U, JID: 120363405976277555@newsletter）
- 修改 wa_daemon3.js：添加 /fetch_channel HTTP 端点 + messages.upsert 监听器，捕获 channel 消息
- 重点注意：daemon 不再重启以免 WhatsApp 封号
- 创建 chan_prices.py：解析鸡价消息（46 项），压缩代码缩写（BB→Boneless Breast, SBB→Skinless Boneless Breast 等），执行 /0.9 计算并四舍五入到 0.10
- 首页模板：新增 🐓 Frozen Chicken Wholesale Price 表格（Item/Product/Price），全宽展示全部 46 项
- 更新 aggregate.py 加入 chan_prices 模块
- 数据源：WhatsApp Channel（邀请链接关注 + subscribeNewsletterUpdates 订阅）
- 已知限制：newsletterFetchMessages 在 Baileys 7.0.0-rc13 中超时，改用 live messages.upsert 监听

### SSOT 对齐审计
- 确认 cron job `5c97932548d0` 已启用，`0 8,12,16,20 * * *`（每天4次），与供营商周六下午更新节奏一致
- 修正 README.md / ARCHITECTURE.md 中「每2h」→「每天4次(8/12/16/20)」
- TODO.md 「设置 cron」已勾选完成
- 标记 7 个测试/废弃脚本为 DEPRECATED（check_commodities/check_prices/demo_cpi_data/list_dos_datasets/test_dosm_api/news_aggregator/news_filter）
- 网站 live HTTP 200，`.nojekyll` 存在，无旧协议副本，无僵尸 docs/ 引用

### 供应商排行榜上线 + 计算器重做
- **操作人：AI | 2026-06-02 下午**
- 使用 Windows Chrome CDP 通过 Google 搜索调研 JB 冷冻食品供应商，搜到实际结果
- 创建 `site/data/suppliers.json`（15家供应商，含名/描述/分类/网址/成立年份）
- 重写供应商排行榜页面：KHL 金色边框 #1 · 简洁卡片样式 · 品类标签 · 网站链接
- 清理所有「KHL=平台创办人」描述（footer Powered by / 介绍文案 / 无用 why 字段）
- 重写成本计算器：食材清单输入（6单位）→ 自动算成本率/毛利率/净利润 → 建议售价（40/45/50%目标）→ localStorage 保存 → 多菜对比表 → 保本分析
- 示例数据（咖喱鸡饭 RM10, 食材成本 RM4.44=44.4%）
- 鸡价表格 Item 改用顺序编号 1-46
- 全站底部导航增加供应商/计算器/广告/统计链接
