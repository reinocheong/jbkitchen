# TODO.md

> **开发信条：** 厨师简历栏 = 免费招聘栏位 → 吸引厨师注册 → 拿到线索 → KHL 销售谈供应。
> KHL 不介入安排厨师工作，不做中介。所有开发以此为准。

## ✅ 已完成

- [x] Hugo 站点骨架 + 深绿金色主题
- [x] 首页（两条路径：找厨师/找工作）
- [x] 成本计算器 V2（菜品成本卡+食材清单+多菜对比+保本分析+建议售价+localStorage保存）
- [x] 供应商排行榜页面（15家真实JB供应商+排名+KHL #1金色卡片）
- [x] 供应商名单通过Windows Chrome Google搜索调研（15家JB冷冻食品供应商）
- [x] 全站清理「KHL=平台创办人」相关表述（footer/描述）
- [x] 鸡价表格 Item 改用顺序编号（1-46），不再显示来源编号
- [x] 供应商目录（KHL 置顶）
- [x] KHL 详情页（产品展示 + WhatsApp 表单）
- [x] 3 篇经营指南
- [x] 厨师简历列表页 + 详情页（6 个样本数据）
- [x] 简历提交表单（WhatsApp 推送）
- [x] GitHub Pages 部署
- [x] 新闻 + 汇率自动采集脚本
- [x] DOSM CPI 数据接入 + Google News RSS 马来西亚餐饮新闻（行业动态板块）✅
- [x] SSOT 文档体系（7 文档）
- [x] 广告合作页面（4 个定价层级 + CPM 公式）**【已移除 — 站点改为 100% 免费】**
- [x] 全站 emoji 清理 — 纯文字专业设计
- [x] 移除广告页面及相关引用（nav/footer/dashboard）
- [x] 供应商商家提交表单（Google Form）
- [x] 页面浏览追踪（CountAPI + GA4 占位）
- [x] 流量统计面板（Dashboard：总访问量、页面排行、广告曝光）
- [x] 首页行业动态板块：汇率 + DOSM CPI + Google News RSS + WhatsApp Channel 鸡价 ✅
- [x] WhatsApp Channel 自动抓取：Baileys 监听频道 → 解析价格 → /0.9 计算 → 网站显示
- [x] setup/ 目录 + SHEET_SETUP_GUIDE.md（Google Sheet 部署指南）
- [x] JB 餐饮招聘聚合：4 大网站 (Jora/Hiredly/Maukerja/MyFutureJobs) + 8 个 Facebook 群组
- [x] 招聘数据 AI 可搜索化：ID、分类、技能、规范化字段（title_normalized/category/skills/location等）
- [x] Hugo list.html 模板更新：分类标签、薪资格式化、来源彩色徽章
- [x] SSOT 7 文档全面更新对齐当前项目状态

## ⏳ 待办

- [ ] 手机部署 Google Apps Script（需要电脑或手机 GAS 编辑）
- [ ] GitHub token 添加 workflow scope → 启用自动化 CI/CD
- [ ] KHL 真实 WhatsApp 号码
- [ ] GA4 Measurement ID 替换为真实 ID
- [ ] 域名购买 `jbkitchen.com`
- [ ] Google Search Console 接入
- [ ] 厨师注册数据导出到 XLSX 功能（通过 Google Sheets 导出）

## ⚠️ 已知问题

- 用户手机 GitHub Pages 白屏（疑似 DNS 缓存/隐私模式可解）
- CountAPI 免费版有请求频率限制
- Google Apps Script 部署需要 Gmail 账号（用户暂时没电脑）
