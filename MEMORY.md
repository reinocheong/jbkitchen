# MEMORY.md

## 已知坑位

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
当前策略：主用 TechCrunch + HN + API fallback 兜底。

### 手机端 GitHub Pages 白屏
用户小米手机访问 GitHub Pages 出现白屏，桌面 Chrome 正常。
可能原因：DNS 缓存、GitHub Pages CDN 节点问题、浏览器兼容性。
排查方向：清缓存、隐私模式、确认 URL 正确。

### CountAPI 免费版限制
CountAPI 免费版有请求频率和存储限制。不能用做精确统计，只适合展示趋势。
长期方案：考虑自建计数或切换到 GA4 为主。
