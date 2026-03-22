---
name: web-research
description: "联网信息获取与网页抓取。关键词：搜索、抓取、调研、爬取、查资料、保存文章、批量采集"
type: tool
version: 1.1.0
---

# Web Research 联网调研

综合信息获取能力，根据场景自动选择最佳工具：搜索、单页抓取、JS渲染抓取、批量爬取。

---

## 触发条件

**搜索类:**
- "搜索一下 XX 的最新信息"
- "帮我查一下 XX 的资料"
- "调研一下 XX 市场/竞品/趋势"

**抓取类:**
- "抓取这个网页的内容"
- "保存这篇文章"
- "提取这个页面的数据"

**批量类:**
- "批量采集竞品信息"
- "爬取这个网站的数据"
- "监控这个页面的更新"

---

## 工具矩阵（核心 2 件套 + 场景扩展）

| 优先级 | 工具 | 适用场景 | 成本 | 可靠性 |
|--------|------|---------|------|--------|
| **P0** | `WebSearch` | 分散信息搜索、最新资讯、多源验证 | 免费（内置） | ⚠️ 网络依赖 |
| **P0** | `WebFetch` | 静态页面快速抓取（博客、新闻、文档） | 免费（内置） | ⚠️ 部分域名受限 |
| **P0** | `Playwright MCP` | JS渲染页面、需要登录/交互、SPA | 免费（本地运行） | ✅ 最可靠 |
| **P1** | `Firecrawl` | 批量/全站爬取、结构化提取、定时监控 | 免费额度+付费 | ✅ 可靠 |

**网络环境提示**：
- Google 搜索在某些网络环境下可能被拦截
- WebFetch 对 GitHub 等域名可能受限
- Playwright 是最可靠的通用方案

---

## 选型决策树（自动选择）

```
开始信息获取
    │
    ├─ 是搜索分散信息？（找资料、查趋势、多源验证）
    │     └─→ WebSearch
    │
    ├─ 是定向抓取特定页面？
    │     │
    │     ├─ 静态页面？（博客、新闻、文档、GitHub）
    │     │     └─→ WebFetch，秒级响应
    │     │
    │     └─ 需要 JS 渲染？（SPA、React/Vue、X/Twitter）
    │           ├─ 需要登录/交互/滚动？
    │           │     └─→ Playwright MCP
    │           └─ 只需内容，不需要交互？
    │                 └─→ Firecrawl 或 Playwright
    │
    ├─ 是批量采集？（多URL、竞品分析、全站爬取）
    │     └─→ Firecrawl（批量/结构化提取）
    │
    └─ 需要定期监控？（价格追踪、内容更新）
          └─→ Firecrawl（调度功能）
```

---

## 各角色典型场景

### CEO

| 场景 | 推荐工具 | 示例 |
|------|---------|------|
| 竞品调研 | WebSearch + WebFetch | 搜索竞品列表，抓取官网定价页 |
| 市场数据 | WebSearch | "AI coding assistant market size 2025" |
| 客户案例 | Firecrawl | 批量抓取竞品客户案例页面 |
| 行业趋势 | WebSearch | "SaaS pricing trends 2025" |

### VibeCoder

| 场景 | 推荐工具 | 示例 |
|------|---------|------|
| 技术文档 | WebFetch | 抓取官方文档特定页面 |
| API 调研 | WebSearch + WebFetch | 搜索对比，抓取详情页 |
| 抓取 SPA 内容 | Playwright | X/Twitter、React 应用数据 |
| 批量采集工具 | Firecrawl | 批量抓取 npm 包信息 |

### DataAnalyst

| 场景 | 推荐工具 | 示例 |
|------|---------|------|
| 行业基准数据 | WebSearch | "SaaS conversion rate benchmark" |
| 验证假设 | WebSearch 多源交叉 | 从2-3个来源验证同一数据 |
| 结构化数据采集 | Firecrawl | 提取表格数据、价格信息 |
| 竞品数据监控 | Firecrawl | 定期抓取竞品定价变化 |

---

## 工具详解

### 1. WebSearch - 信息搜索

**用途**: 通过搜索引擎查找分散信息，获取最新资讯

**工具**: `WebSearch(query, allowed_domains?, blocked_domains?)`

**示例**:
```
WebSearch("Claude Code alternatives 2025")
WebSearch("AI coding assistant market size", allowed_domains=["techcrunch.com", "theverge.com"])
```

**最佳实践**:
- 最新信息加年份: `"XX 2025"`
- 对比搜索: `"XX vs YY comparison"`
- 官方文档: `"XX documentation official"`

---

### 2. WebFetch - 静态页面抓取

**用途**: 快速抓取静态页面内容（博客、新闻、文档）

**工具**: `WebFetch(url, prompt)`

**示例**:
```
WebFetch("https://example.com/article", "提取文章标题、正文、发布时间")
```

**适用场景**:
- 博客文章保存
- 新闻内容提取
- 文档页面抓取
- GitHub README 读取

**限制**:
- 不支持 JS 渲染（React/Vue/SPA 不行）
- 不能处理登录态

---

### 3. Playwright MCP - JS 渲染与交互

**用途**: 抓取 SPA 页面、需要登录或交互的场景

**配置要求**:
```json
{
  "mcpServers": {
    "playwright": {
      "command": "npx",
      "args": ["-y", "@anthropic-ai/playwright-mcp"]
    }
  }
}
```

**适用场景**:
- X/Twitter 等 SPA
- 需要登录的页面
- 需要滚动/点击交互
- 验证码处理（人工介入）

**示例**:
```
"用 Playwright 打开 https://x.com/elonmusk/status/xxx，
抓取：推文内容、发布时间、互动数据（转/赞/评），
返回 JSON 格式"
```

---

### 4. Firecrawl - 批量与结构化爬取

**用途**: 批量 URL、全站爬取、结构化提取、定时监控

**配置要求**:
```json
{
  "mcpServers": {
    "firecrawl": {
      "command": "npx",
      "args": ["-y", "firecrawl-mcp"],
      "env": {
        "FIRECRAWL_API_KEY": "your-api-key"
      }
    }
  }
}
```

**适用场景**:
- 批量竞品信息采集
- 全站内容爬取
- 结构化数据提取（价格、功能等）
- 定期监控（价格变动、内容更新）

**示例**:
```
"用 Firecrawl 爬取 https://competitor.com/pricing，
提取：产品名称、定价方案、功能列表，
返回结构化 JSON"
```

---

## 典型场景操作指南

### 场景 1：保存一篇好文章

**判断流程**:
```
用户: "保存这篇文章 https://..."
    ↓
尝试 WebFetch（最快）
    ↓
成功？→ 返回格式化内容
失败？→ 可能是 SPA → 使用 Playwright
```

**执行**:
```
"用 WebFetch 抓取 https://blog.example.com/article，
提取标题、作者、发布时间、正文内容，
保存为 Markdown 格式"
```

---

### 场景 2：抓取推文/X 帖子

**必须 Playwright**（X 是 SPA，需要 JS 渲染）:

```
"用 Playwright 打开 https://x.com/username/status/123456，
等待推文加载完成后抓取：
1. 推文内容（文本）
2. 发布时间
3. 互动数据（转发数、点赞数、回复数）
4. 图片/视频链接（如有）
返回 JSON 格式"
```

**批量抓取多条**:
```
"用 Playwright 依次打开以下 X 帖子链接：
- https://x.com/user1/status/111
- https://x.com/user2/status/222
- https://x.com/user3/status/333

提取每条的内容和互动数据，汇总成表格输出"
```

---

### 场景 3：批量采集竞品信息

**推荐 Firecrawl**:

```
"用 Firecrawl 爬取以下竞品定价页面：
- https://competitor1.com/pricing
- https://competitor2.com/pricing
- https://competitor3.com/pricing

提取结构化数据：
{
  "product_name": "...",
  "pricing_tiers": [...],
  "key_features": [...],
  "free_tier_available": true/false
}

汇总对比表格输出"
```

**全站爬取**:
```
"用 Firecrawl 全站爬取 https://docs.example.com，
提取所有 API 端点文档，
输出结构化数据"
```

---

### 场景 4：搜索+抓取组合调研

**典型流程**:
```
用户: "调研 AI 编码助手市场"
    ↓
Step 1: WebSearch 找主要玩家
        "AI coding assistant market leaders 2025"
    ↓
Step 2: WebSearch 找市场数据
        "AI coding tools market size growth 2025"
    ↓
Step 3: WebFetch/Playwright 抓取竞品官网
        抓取定价页、功能页
    ↓
Step 4: Firecrawl 批量采集（如需要）
        批量抓取多个竞品详情
    ↓
综合输出结构化报告
```

---

## 质量与可信度规范

### 来源可信度评估

| 等级 | 来源类型 | 示例 |
|------|---------|------|
| **高** | 官方文档、GitHub、权威媒体 | anthropic.com, github.com, TechCrunch |
| **中** | 技术博客、论坛讨论 | Medium, Dev.to, Stack Overflow |
| **低** | 内容农场、未知名网站 | 需交叉验证 |

### 关键信息交叉验证

对于重要数据，至少从 2-3 个独立来源验证：

```
用户询问："Claude Code 的竞品市场份额"

→ WebSearch: "Cursor market share AI coding"
→ WebSearch: "GitHub Copilot vs Claude Code usage"
→ WebFetch: 抓取权威报告原文

综合：如果来源一致 → 高可信度；不一致 → 说明分歧
```

### 输出引用格式

```markdown
根据搜索结果 [1][2] 和抓取数据 [3]：

- AI 编码助手市场规模约 XX 亿美元 [1]
- 主要玩家包括 Cursor、GitHub Copilot、Claude Code [2]
- Cursor 定价为 $20/月（抓取自官网）[3]

---
**来源:**
[1] [报告标题](URL) - TechCrunch
[2] [对比文章](URL) - The Verge
[3] [Cursor 定价页](https://cursor.com/pricing) - 抓取时间: 2025-03-05
```

---

## MCP 配置检查清单

使用前确认 MCP 配置：

```bash
# 检查 Playwright MCP 是否配置
grep -A 5 "playwright" ~/.claude/config.json 2>/dev/null || echo "未配置 Playwright MCP"

# 检查 Firecrawl MCP 是否配置
grep -A 5 "firecrawl" ~/.claude/config.json 2>/dev/null || echo "未配置 Firecrawl MCP"
```

**未配置时提示用户**:
```
需要配置 Playwright MCP 才能抓取 SPA 页面。

配置步骤：
1. npm install -g @anthropic-ai/playwright-mcp
2. npx playwright install chromium
3. 添加到 ~/.claude/config.json

详见：/Users/adam/.claude/skills/web-references/mcp-setup.md
```

---

## 注意事项

### 1. 工具选择优先级

- **能用 WebFetch 就不用 Playwright**（更快更稳定）
- **能用简单搜索就不用复杂抓取**（先验证需求）
- **批量场景优先考虑 Firecrawl**（效率更高）

### 2. 避免滥用

- **不要**用 Playwright 抓取纯静态页面（杀鸡用牛刀）
- **不要**频繁抓取同一网站（注意频率限制）
- **不要**抓取需要付费/登录的敏感内容（合规问题）

### 3. 隐私与安全

- 搜索关键词可能被记录，敏感信息脱敏
- 登录态抓取消耗后及时清理
- 遵守目标网站的 robots.txt 和使用条款

---

## 故障排除指南

### WebSearch 失败（API 错误或超时）

**症状**: `API Error: 400` 或超时

**解决策略**:
1. 切换到 Playwright 直接抓取搜索引擎结果页
2. 使用多个关键词并行搜索，取交集
3. 直接抓取目标网站而非依赖搜索

**示例代码**:
```python
# Playwright 替代 WebSearch
page.goto("https://www.google.com/search?q=keyword",
          wait_until="domcontentloaded")
results = page.locator("#search .g").all()
```

---

### WebFetch 失败（域名受限）

**症状**: `Unable to verify if domain is safe to fetch`

**常见受限域名**: GitHub、某些企业官网

**解决策略**:
1. 使用 Playwright 替代（最可靠）
2. 尝试抓取页面的简化版本（raw content）
3. 使用 Firecrawl（如果已配置）

**降级流程**:
```
WebFetch 失败
    ↓
尝试 Playwright 抓取
    ↓
成功 → 返回内容
失败 → 提示用户手动提供内容或更换源
```

---

### Playwright 选择器失败

**症状**: `strict mode violation` 或 `TimeoutError`

**常见原因**:
- 选择器匹配多个元素
- 页面结构变化
- 页面未完全加载

**解决方案**:
```python
# 使用 first/last/nth 限定
page.locator("h1.heading-element").first.text_content()

# 使用 wait_for_selector 等待元素
page.wait_for_selector("article.markdown-body", timeout=10000)

# 使用更宽松的选择器
page.locator("text=关键词").first
```

---

### 中国大陆网络环境

**常见问题**:
- Google 搜索被拦截
- 某些国外网站访问缓慢

**应对策略**:
1. **优先使用 Playwright** 直接抓取目标网站
2. **使用国内搜索引擎**（如百度搜索结果页）
3. **多源验证** 时优先选择国内可访问的源
4. **企业官网** 通常访问正常，可直接抓取

**推荐优先级调整**:
```
中国大陆网络环境:
    WebSearch (Google) → 可能失败
    WebFetch → 部分受限
    Playwright → ✅ 最可靠
    Firecrawl → ✅ 可靠
```

---

## Playwright 详细模板

### 基础页面抓取模板

```python
from playwright.sync_api import sync_playwright

def scrape_page(url, selector=None):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1440, "height": 900})

        # 使用 domcontentloaded 更快，networkidle 更完整
        page.goto(url, wait_until="domcontentloaded", timeout=30000)

        # 等待特定元素（如果有）
        if selector:
            page.wait_for_selector(selector, timeout=10000)

        # 提取内容
        content = page.locator("body").inner_text()
        title = page.title()

        browser.close()
        return {"title": title, "content": content}
```

### 多页面抓取模板

```python
def scrape_multiple(urls, extract_fn):
    """批量抓取多个页面"""
    results = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        for url in urls:
            try:
                page.goto(url, wait_until="domcontentloaded", timeout=30000)
                data = extract_fn(page)
                results.append({"url": url, "data": data, "success": True})
            except Exception as e:
                results.append({"url": url, "error": str(e), "success": False})

        browser.close()
    return results
```

### 处理 SPA（单页应用）

```python
# X/Twitter、React 应用等需要等待 JS 渲染
page.goto(url, wait_until="networkidle", timeout=30000)

# 等待特定元素出现
page.wait_for_selector("[data-testid='tweet']", timeout=10000)

# 滚动加载更多内容（如需）
for _ in range(3):
    page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
    page.wait_for_timeout(1000)
```

---

## 多源验证实战流程

当需要验证关键信息时，使用多工具交叉验证：

```
用户询问："XX 公司的最新融资信息"

Step 1: WebSearch（快速概览）
    → "XX company funding 2025"
    → 如果失败，跳到 Step 2

Step 2: Playwright 抓取多个源
    → 抓取公司官网新闻页
    → 抓取 Crunchbase/IT桔子
    → 抓取行业媒体报道

Step 3: 交叉验证
    → 源 A: 官网融资公告
    → 源 B: 媒体报道
    → 源 C: 工商信息变更

Step 4: 输出
    → 信息一致 → 高可信度
    → 信息冲突 → 标注分歧点
```

---

## 质量检查清单（更新版）

- [ ] 信息来源是否可靠？（官网>媒体>论坛）
- [ ] 关键数据是否有 2-3 个独立来源验证？
- [ ] 是否标注了信息获取时间？
- [ ] 是否说明了信息的不确定性？
- [ ] 如果工具失败，是否尝试了备用方案？
- [ ] 截图/数据是否已保存到 cache 文件夹？

---

## 快速参考卡（v1.1）

| 你想做 | 首选工具 | 备用方案 | 命令示例 |
|--------|---------|---------|---------|
| 搜索信息 | WebSearch | Playwright+Bing/Google | `"搜索 XX 的最新信息"` |
| 保存文章 | WebFetch | Playwright | `"抓取这篇文章保存为 Markdown"` |
| GitHub 项目 | Playwright | WebFetch raw | `"抓取 GitHub 项目信息"` |
| 企业官网 | WebFetch/Playwright | - | `"调研 XX 公司"` |
| 抓取 X/Twitter | Playwright | - | `"用 Playwright 抓取这条推文"` |
| 批量竞品采集 | Firecrawl | Playwright 循环 | `"用 Firecrawl 批量抓取"` |
| 全站爬取 | Firecrawl | - | `"全站爬取 example.com"` |

**故障速查**:
- WebSearch 失败 → 用 Playwright 直接抓搜索页
- WebFetch 受限 → 换 Playwright
- Playwright 超时 → 换 `wait_until="domcontentloaded"`

---

*Web Research Skill v1.1.0 | Aidam 3.0.5*
*更新：增加故障排除、中国大陆网络适配、详细模板*
