# ARCHITECTURE.md

> **开发信条：** 厨师简历栏 = 免费招聘栏位 → 吸引厨师注册 → 拿到线索 → KHL 销售谈供应。
> KHL 不介入安排厨师工作，不做中介。所有开发决策以此为准。

## 系统拓扑

```mermaid
graph TD
    subgraph "数据采集层 (Python)"
        NA[news_aggregator.py<br/>RSS 新闻采集] --> DATA[(data/*.json)]
        PT[price_tracker.py<br/>汇率 API] --> DATA
        AG[aggregate.py<br/>主调度器] --> NA
        AG --> PT
    end

    subgraph "表单录入层 (Google)"
        FORM[厨师提交表<br/>site/chefs/submit/] -->|WhatsApp| KHL_PHONE[KHL WhatsApp]
        FORM -->|Google Apps Script| SHEET[(Google Sheet)]
    end

    subgraph "数据层"
        DATA --> SYNC[同步到 site/data/]
        SITE_DATA[(site/data/*.json)] --> HUGO
        CHEFS_JSON[site/data/chefs.json<br/>手动维护] --> HUGO
    end

    subgraph "展示层 (Hugo)"
        MD[content/*.md<br/>指南/供应商/厨师] --> HUGO
        HUGO[Hugo Build] --> HTML[docs/ 静态页面]
    end

    subgraph "外部服务"
        HTML --> CI[CountAPI<br/>每页独立计数]
        HTML --> GA[(GA4<br/>埋点)]
    end

    subgraph "部署"
        HTML --> GH[GitHub Pages<br/>/docs 目录]
        GH --> USER[访客<br/>厨师/老板/供应商]
    end

    subgraph "引流链路"
        USER -->|搜到 SEO 内容| SITE[网站页面]
        SITE -->|供应商目录| KHL[KHL 详情页]
        KHL -->|WhatsApp 询价| LEAD[KHL 销售跟进]
        SITE -->|简历浏览| CONTACT[老板直接联系厨师]
        LEAD_SALES[KHL 销售] -->|从 Sheet 获取线索| CONTACT_CHEF[联系厨师谈供应]
    end
```

## 数据流向

```
RSS 源 / 汇率 API
    ↓ (手动构建)
Python 采集 → data/*.json
    ↓
site/data/*.json → Hugo 读取
    ↓
手动 Hugo 构建 → docs/ 输出
    ↓
git push → GitHub Pages

厨师表单:
网站提交 → WhatsApp 通知老板
        → Google Sheet 记录存档
```

## 页面计数

```
每个页面加载时:
CountAPI hit → 存到云端计数器
Dashboard 读取: CountAPI get → 按流量排序展示
GA4: 标准 page_view 事件（需替换真实 Measurement ID）
```

## 模块依赖

```
aggregate.py  ← 依赖 ← news_aggregator.py
aggregate.py  ← 依赖 ← price_tracker.py
Hugo layouts   ← 读取 ← site/data/*.json（运行时）
Hugo layouts   ← 读取 ← site/data/chefs.json（手动维护）
无循环依赖。所有数据单向流动。
```
