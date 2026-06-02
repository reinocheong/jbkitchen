# MEMORY.md

> **开发信条：** 厨师简历栏 = 免费招聘栏位 → 吸引厨师注册 → 拿到线索 → KHL 销售谈供应。
> KHL 不介入安排厨师工作，不做中介。避坑记录以此为准。

## 已知坑位

### 用户明确拒绝 emoji — 用纯文字 + SVG 几何图案
用户明确要求所有界面不得使用 emoji（"they make it look cheap"）。
设计方案：纯文字界面，工具卡片使用 36px 彩色方块 + 白色 SVG 几何图案作为图标。
导航/按钮/标签等使用纯文字。
所有 emoji 在模板中替换为 SVG 或留空。

### CSS 大括号未闭合 — 最隐蔽的 CSS bug
`.source-badge {` 第 369 行未闭合 → 第 370~848 行全部被嵌套进 `.source-badge` 内
症状：所有样式失效（紫色链接、无边框、位置散乱），但无 JS 报错
修复：找到未闭合的大括号并闭合，重新定义被发现丢失的 hero-btn 等 class
教训：CSS 大括号未闭合是最危险的 bug——不会报错，只是后续样式全失效

### GitHub Pages CDN 缓存 — CSS 更新后需版本号
更改 CSS/HTML 后，GitHub Pages CDN 会缓存旧版本 ~1-2 分钟
修复：在 CSS 链接加 ?v3 版本号：`<link href="/css/chef.css?v3">`
下次更新时递增版本号（?v4, ?v5…）

### Google Translate 顶部横幅适配问题
Google Translate 默认顶部横幅在手机端很丑
修复：改为导航栏右侧小地球 SVG 图标，点击弹出语言选择列表
关键：用 `googleTranslateElementInit` 配置 `layout: google.translate.TranslateElement.InlineLayout.SIMPLE`

### 手机端导航 — 汉堡菜单替代两行导航
两行导航在手机端太丑
实现：三条横线 SVG → 点击展开全屏菜单（带 fade-in 动画）→ X 图标关闭
CSS 用 `@media (max-width: 768px)` 隐藏桌面 nav，显示汉堡按钮



### Maukerja Nuxt.js SSR — 需 Playwright
Maukerja.my 使用 Nuxt.js 服务端渲染，初始 HTML 不含职位数据。
`requests` 拿到的是空白骨架，需要 Playwright 等待 `networkidle` 后从 DOM 提取。

### MyFutureJobs Angular SPA — 需 Playwright + 滚动
MyFutureJobs 是 Angular SPA，使用虚拟滚动（virtual scrolling）加载职位。
需要 JavaScript 自动滚动到底部并等待加载完成（约 5 秒）才能获取全部职位。

### GitHub Pages 部署延迟 ~1-2 分钟
`git push` 后 GitHub Pages 需要 1-2 分钟重新构建。
立即访问可能看到旧内容，属于正常延迟。



### GitHub token 缺少 workflow scope
Token 不支持 push workflow 文件（`.github/workflows/*.yml`）。
解法：重新生成带 `workflow` scope 的 token，然后从 git history 恢复 workflow 文件。
当前状态：`.github/workflows/` 目录不存在，完全手动构建推送。

### Bing/Google 搜索"frozen food"返回迪士尼电影
"frozen" 一词在英文搜索引擎中优先匹配 Disney Frozen。
必须用 `冷冻食品` 中文搜索或 `"frozen food" johor` 精确匹配。

### Hugo publishDir
设置 `publishDir = "../docs"` 后，构建输出到项目根目录的 `docs/`，而非 `site/public/`。
CI 中 git push 会自动推送 `docs/` 内容。

### 新闻 RSS 源不可靠
部分马来西亚 RSS 源（BERNAMA 等）经常超时或返回空。
当前策略：使用 Google News RSS（22 个马来西亚餐饮关键词，4 大类），feedparser 解析，稳定可用。
取代原 TechCrunch + HN + API fallback 兜底方案。

### DOSM API 数据限制
- cpi_headline API 返回 1980 年至今的月度 CPI 指数，limit=5000 才能取到最新数据
- 部分 division（如 08 通讯）在 index API 中更新滞后（至 2025-12），而 inflation API 已到 2026-04
- 无 division 11（餐饮住宿），实际只使用 overall/01/04/07/08

### 手机端 GitHub Pages 白屏 — 需 .nojekyll
用户小米手机访问 GitHub Pages 出现白屏，桌面 Chrome 正常。
**根因：** Hugo 非 Jekyll 站点缺少 `.nojekyll` 文件 → GitHub Pages 运行 Jekyll 处理 docs/ 目录，输出空壳页面。
**修复：** 在 docs/ 目录添加 `.nojekyll` 文件（空文件），禁止 Jekyll 处理。
**教训：** 任何非 Jekyll 站点（Hugo、纯 HTML/CSS 等）用 GitHub Pages 部署时，必须在源目录放 `.nojekyll`。

### CountAPI 免费版限制
CountAPI 免费版有请求频率和存储限制。不能用做精确统计，只适合展示趋势。
长期方案：考虑自建计数或切换到 GA4 为主。

### WhatsApp Baileys newsletterFetchMessages 超时
`newsletterFetchMessages(jid, count)` 在 Baileys 7.0.0-rc13 中发送 IQ 查询后无响应，最终超时。
当前方案：改用 `subscribeNewsletterUpdates(jid)` + `messages.upsert` 事件监听实时消息。
不重启 daemon — 频繁重启会触发 WhatsApp 封号限制。

### 鸡价解析：名称清理规则
- 保留英文名，缩写展开（BB → Boneless Breast, SBB → Skinless Boneless Breast 等）
- 品牌名保持大写（CARGIL, TYSON）
- 价格 /0.9 → 四舍五入到 0.10（13.88889 → 13.90）
- 原始消息存 `chan_raw.json`，解析后存 `chan_prices.json`
- 不显示 Source Price 列，只看调整后价格
- 供营商通常周六下午更新价目表，cron 每天 8/12/16/20 点自动解析上线

### 全站英文化后 Google Translate 备用
站点主要语言为英文，右上角 Google Translate 小图标供中文/马来文用户切换。
注意：Google Translate 自动翻译无法保证 100% 准确，专业术语建议在原文旁标注。
