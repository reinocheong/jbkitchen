# DEPLOY.md

## 当前部署

| 项目 | 值 |
|------|-----|
| 平台 | GitHub Pages |
| URL | https://reinocheong.github.io/jbkitchen/ |
| 源目录 | `/docs`（main 分支） |
| 正式域名 | 待购买（`jbkitchen.com`） |

## 部署流程

### 手动构建
```bash
cd site
hugo --minify    # 输出到 ../docs/
git add -A && git commit && git push
```

### 自动部署（TODO：需添加 workflow scope 的 token）

当前 GitHub token 缺少 `workflow` scope，无法 push workflow 文件。
解决后启用 `.github/workflows/deploy.yml` 和 `aggregate.yml`。

## 环境变量

无环境变量。所有配置硬编码在 `hugo.toml` 和 Python 脚本中。

## 数据同步

Python 脚本自动双向同步：
- `data/*.json` → 原始数据
- `site/data/*.json` → Hugo 读取的数据

两个目录内容始终一致（`aggregate.py` 在写入时同步到两边）。
