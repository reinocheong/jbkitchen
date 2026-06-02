# JOURNAL.md

> **开发信条：** 厨师简历栏 = 免费招聘栏位 → 吸引厨师注册 → 拿到线索 → KHL 销售谈供应。
> KHL 不介入安排厨师工作，不做中介。开发日志保持与此一致。

## 2026-06-02

**操作人：AI**

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
