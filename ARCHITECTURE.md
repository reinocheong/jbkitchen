# ARCHITECTURE.md

## 系统拓扑

```mermaid
graph TD
    subgraph "数据采集层 (Python)"
        NA[news_aggregator.py<br/>RSS 新闻采集] --> DATA[(data/*.json)]
        PT[price_tracker.py<br/>汇率 API] --> DATA
        AG[aggregate.py<br/>主调度器] --> NA
        AG --> PT
    end

    subgraph "数据层"
        DATA --> SYNC[同步到 site/data/]
    end

    subgraph "展示层 (Hugo)"
        SYNC --> HUGO[Hugo Build]
        MD[content/*.md<br/>指南文章] --> HUGO
        HUGO --> HTML[docs/ 静态页面]
    end

    subgraph "部署"
        HTML --> GH[GitHub Pages]
        GH --> USER[餐厅老板]
    end

    subgraph "引流链路"
        USER -->|搜到 SEO 内容| SITE[网站页面]
        SITE -->|供应商目录| KHL[KHL 详情页]
        KHL -->|留下联系方式| LEAD[KHL 销售跟进]
    end
```

## 数据流向

```
RSS 源 / 汇率 API
    ↓ (每 12h GitHub Actions)
Python 采集 → data/*.json
    ↓ (同步)
site/data/*.json → Hugo 读取 → 静态页面
    ↓ (自动部署)
GitHub Pages → 用户浏览器
```

## 模块依赖

```
aggregate.py  ← 依赖 ← news_aggregator.py
aggregate.py  ← 依赖 ← price_tracker.py
Hugo layouts   ← 读取 ← site/data/*.json （运行时）
```

无循环依赖。所有数据单向流动。
