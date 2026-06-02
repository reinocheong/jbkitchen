# MEMORY.md

## 已知坑位

### GitHub token 缺少 workflow scope
Token 不支持 push workflow 文件（`.github/workflows/*.yml`）。
解法：重新生成带 `workflow` scope 的 token，或先删除 workflow 文件再 push（已在 jbkitchen 中这么做了）。
当前：workflow 文件在本地但被 git ignored，需要手动重新添加。

### Bing/Google 搜索"frozen food"返回迪士尼电影
"frozen" 一词在英文搜索引擎中优先匹配 Disney Frozen。
必须用 `冷冻食品` 中文搜索或 `"frozen food" johor` 精确匹配。

### Hugo publishDir
设置 `publishDir = "../docs"` 后，构建输出到项目根目录的 `docs/`，而非 `site/public/`。

### 新闻 RSS 源不可靠
部分马来西亚 RSS 源（BERNAMA 等）经常超时或返回空。
当前策略：主用 TechCrunch + HN + API fallback 兜底。
