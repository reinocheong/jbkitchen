# TODO.md

## Phase 1 — MVP ✅ 已完成

- [x] Hugo 站点骨架搭建
- [x] 首页模板 + Hero + 功能卡片 + KHL 推荐位
- [x] 成本计算器（纯前端 JS）
- [x] 供应商目录页面（KHL 置顶 + 占位卡片）
- [x] KHL 详情页（产品展示 + WhatsApp 表单）
- [x] CSS 主题（深绿 + 金色）
- [x] 3 篇指南（清真认证 / 执照 / 冷冻采购）
- [x] GitHub Pages 部署（`/docs` 目录）
- [x] 汇率自动采集（免费 API）
- [x] 新闻自动采集（RSS + Hacker News API）
- [x] 聚合脚本（`aggregate.py` 一键跑）

## Phase 2 — SSOT 文档 ✅ 已完成

- [x] README.md
- [x] ARCHITECTURE.md
- [x] DEPLOY.md
- [x] USER.md
- [x] TODO.md
- [ ] JOURNAL.md
- [ ] MEMORY.md

## Phase 3 — 合规修正（进行中）

- [ ] 拆 `news_aggregator.py` → 模块化（≤150 行）
- [ ] 添加 `.logs/error.log` 双日志
- [ ] `scripts/requirements.txt`
- [ ] git 移除已被 `.gitignore` 覆盖的旧 `docs/` 提交

## Phase 4 — 后续

- [ ] GitHub token 添加 workflow scope 启用自动化部署
- [ ] 供应商名单补全（需要 Reino 提供）
- [ ] KHL 真实 WhatsApp 号码
- [ ] 域名购买 `jbkitchen.com`
- [ ] Google Search Console 接入
- [ ] 新闻 RSS 源补充（马来西亚本地餐饮源）
