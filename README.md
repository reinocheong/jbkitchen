# jbkitchen

新山餐饮经营工具站 — 成本计算器、供应商目录、经营指南

## 项目结构

```
jbkitchen/
├── site/              # Hugo 静态站点
│   ├── content/       # 内容页面 (Markdown)
│   ├── layouts/       # HTML 模板
│   ├── static/        # CSS/JS 等静态资源
│   ├── data/          # 自动生成的 JSON 数据
│   └── hugo.toml      # Hugo 配置
├── scripts/           # Python 自动化脚本（后续添加）
├── data/              # 原始数据（后续添加）
├── resources/         # 下载模板文件（后续添加）
└── .github/workflows/ # GitHub Actions 部署
```

## 本地开发

```bash
cd site
hugo server -D
```

## 部署

推送 main 分支 → GitHub Actions 自动构建并部署到 GitHub Pages。

域名：jbkitchen.com（待购买）

## 引流目标

通过 SEO 内容吸引新山餐饮从业者 → 自然引导至 KHL Frozen Food 供应商页面 → 获取报价 → 销售跟进。
