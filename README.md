# jbkitchen — 新山餐饮经营工具站

> RESTAURANT 经营工具 + 自动内容引流 → KHL Frozen Food

## 一句话定位

不为做"最大的信息站"，做"最有用的餐饮经营工具站"——成本计算器、供应商目录、经营指南，自动更新内容，自然引导餐厅老板到 KHL。

## 商业模式

免费工具站 → SEO 自然流量 → 供应商目录 KHL 置顶 → 详情页留下联系方式 → KHL 销售跟进。

不是内容媒体，是**获客工具**。

## 技术栈

| 层 | 技术 |
|---|------|
| 生成器 | Hugo v0.145 (extended) |
| 数据采集 | Python 3.11 + feedparser + requests |
| 部署 | GitHub Pages（`/docs` 目录） |
| 自动化 | GitHub Actions（每 12h） |
| 域名 | 开发期 `reinocheong.github.io/jbkitchen` 正式期 `jbkitchen.com` |

## 项目目录

```
jbkitchen/
├── site/           # Hugo 静态站点
│   ├── content/    # 指南文章（Markdown）
│   ├── layouts/    # 模板（Go HTML）
│   ├── static/     # CSS
│   ├── data/       # 自动生成的 JSON 数据
│   └── hugo.toml   # Hugo 配置
├── scripts/        # Python 自动化
├── data/           # 原始 JSON 数据
├── docs/           # 构建输出（GitHub Pages 源）
└── .github/workflows/  # CI/CD
```

## 关键约定

- 单脚本 ≤150 行
- 数据 JSON 写入 `data/` 和 `site/data/`（双向同步）
- 新闻 RSS 源必须经过餐饮关键词过滤
- KHL 置顶在所有供应商列表第一位
