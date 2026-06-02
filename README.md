# jbkitchen — 新山餐饮人才与经营平台

> 厨师找工作 · 老板找人才 · 餐厅找供应商 → KHL Frozen Food

## 一句话定位

新山餐饮双面市场平台：厨师挂简历找工作，餐厅老板找人才+找供应商+算成本，自然引导到 KHL。

## 商业模式

```
免费平台：
  ① 厨师免费挂简历 → 餐厅老板自己联系厨师（KHL 不介入）
  ② KHL 销售拿到厨师资料 → 联系谈食材供应合作
  ③ 供应商目录（KHL 置顶 ⭐） + 成本计算器 + 指南 → 吸引餐厅老板
```

**用这个公式理解：** 厨师简历栏 = 招聘栏位 ⟶ 吸引厨师注册 ⟶ 拿到线索 ⟶ KHL 销售谈供应

## 技术栈

| 层 | 技术 |
|---|------|
| 生成器 | Hugo v0.145 (extended) |
| 数据采集 | Python 3.11 + feedparser + requests |
| 数据源 | DOSM Open API（CPI 指数+通胀率）, exchangerate-api.com（汇率）, Google News RSS（新闻） |
| 部署 | GitHub Pages（`/docs` 目录，main 分支） |
| 自动化 | 手动构建推送（token 缺少 workflow scope） |
| 计数 | CountAPI（免费云端计数） |
| 表单 | Google Apps Script → Google Sheets（厨师注册） |
| 域名 | 当前 `reinocheong.github.io/jbkitchen`，正式期 `jbkitchen.com` |

## 项目目录

```
jbkitchen/
├── site/             # Hugo 源码
│   ├── content/      # Markdown 页面
│   ├── layouts/      # Go HTML 模板
│   ├── static/       # CSS
│   ├── data/         # Hugo 读取的 JSON（含自动+手动数据）
│   └── hugo.toml     # Hugo 配置
├── scripts/          # Python 自动化（新闻/汇率采集）
├── data/             # 原始 JSON（自动采集结果）
├── docs/             # 构建输出 → GitHub Pages
├── setup/            # 部署/集成指南（如 GAS Sheet 设置）
├── README.md         # ← 你现在在这
├── ARCHITECTURE.md   # 系统拓扑
├── DEPLOY.md         # 部署流程
├── TODO.md           # 开发状态
├── JOURNAL.md        # 开发日志
├── MEMORY.md         # 踩坑记录
└── USER.md           # 用户画像
```

## 核心页面

| 页面 | 功能 | 目标用户 |
|------|------|---------|
| `/` | 首页：两条路径(找厨师/找工作) | 所有人 |
| `/chefs/` | 厨师简历列表+详情 | 餐厅老板 |
| `/chefs/submit/` | 厨师免费挂简历（→WhatsApp→Sheet） | 厨师 |
| `/suppliers/` | 供应商目录（KHL 置顶） | 餐厅老板 |
| `/suppliers/khl-frozen-food/` | KHL 详情+询价表单 | 潜在客户 |
| `/calculator/` | 成本计算器（纯前端 JS） | 准备/已开餐厅 |
| `/guides/` | 经营指南（清真认证/执照/采购） | 准备开餐厅 |
| `/advertise/` | 广告合作（4 个定价层级+CPM 公式） | 供应商/广告主 |
| `/dashboard/` | 流量统计面板 | jbkitchen 运营 |

## 关键约定

- 单脚本 ≤150 行
- 新闻 RSS 源必须经过餐饮关键词过滤
- KHL 在所有供应商列表排第一位，带 ⭐ 标签
- 所有指南底部有 KHL CTA
- 广告定价：CPM 公式（流速÷1000×位置系数×RM 10）
- 厨师注册数据流向：网站表单 → WhatsApp 通知 → Google Sheet 记录
