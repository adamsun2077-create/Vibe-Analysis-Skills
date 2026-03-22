---
name: warm-minimal-dashboard
description: "暖色极简风数据看板生成。关键词：暖色看板、极简风格、数据可视化、dashboard、图表生成、报告配色"
metadata:
  type: implementation
  version: 1.0.0
---

# 暖色极简风数据看板

适合截图发社交媒体的可视化模板。

## 触发条件

- 需要生成数据分析的可视化看板
- 需要制作适合社交媒体传播的数据图表
- 需要一致的报告配色风格

## 暖色极简配色规范

### 主色调

| 用途 | 色值 | 说明 |
|------|------|------|
| 背景 | `#FAF8F5` | 米白色，纸质感 |
| 主色 | `#2C3E50` | 深灰蓝，主要文字和图表 |
| 强调色 | `#E07A5F` | 赭石橙，重点标注 |
| 辅助色1 | `#81B29A` | 灰绿，次要数据 |
| 辅助色2 | `#F2CC8F` | 暖黄，高亮 |
| 辅助色3 | `#3D405B` | 深墨蓝，标题 |

### 配色比例

```
背景 70% | 主色 20% | 强调色 5% | 辅助色 5%
```

### 渐变方案

```css
/* 强调渐变 */
background: linear-gradient(135deg, #E07A5F 0%, #F2CC8F 100%);

/* 辅助渐变 */
background: linear-gradient(135deg, #81B29A 0%, #3D405B 100%);
```

## 字体规范

| 层级 | 字体 | 大小 | 字重 |
|------|------|------|------|
| 大标题 | system-ui | 32px | 700 |
| 章节标题 | system-ui | 20px | 600 |
| 正文 | system-ui | 14px | 400 |
| 数据标签 | system-ui | 12px | 500 |
| 注释 | system-ui | 11px | 400 |

## 必含图表类型

### 1. 排名条形图

```python
import plotly.graph_objects as go

fig = go.Figure()

fig.add_trace(go.Bar(
    x=df['value'],
    y=df['category'],
    orientation='h',
    marker_color='#E07A5F',  # 强调色
    text=df['value'].round(2),
    textposition='outside'
))

fig.update_layout(
    title=dict(text='Top 10 排名', font=dict(size=20, color='#3D405B')),
    plot_bgcolor='#FAF8F5',
    paper_bgcolor='#FAF8F5',
    font=dict(family='system-ui', color='#2C3E50'),
    xaxis=dict(showgrid=True, gridcolor='#E8E6E3'),
    yaxis=dict(showgrid=False),
    margin=dict(l=150, r=50, t=80, b=50)
)
```

### 2. 散点图（核心图表）

```python
fig = go.Figure()

fig.add_trace(go.Scatter(
    x=df['x_var'],
    y=df['y_var'],
    mode='markers+text',
    marker=dict(
        size=12,
        color='#81B29A',
        line=dict(width=1, color='#3D405B')
    ),
    text=df['label'],
    textposition='top center'
))

# 添加趋势线
fig.add_trace(go.Scatter(
    x=df['x_var'],
    y=trend_line,
    mode='lines',
    line=dict(color='#E07A5F', dash='dash'),
    name='趋势线'
))

fig.update_layout(
    title=dict(text='暴露度 × 薪资关系', font=dict(size=20, color='#3D405B')),
    xaxis_title='AI 暴露度',
    yaxis_title='薪资水平',
    plot_bgcolor='#FAF8F5',
    paper_bgcolor='#FAF8F5',
    showlegend=True
)
```

### 3. 分位对比图

```python
# 箱线图或分组柱状图
fig = go.Figure()

for i, group in enumerate(['高暴露', '中暴露', '低暴露']):
    fig.add_trace(go.Box(
        y=df[df['group']==group]['wage'],
        name=group,
        marker_color=['#E07A5F', '#81B29A', '#F2CC8F'][i]
    ))

fig.update_layout(
    title='不同暴露度群体的薪资分布',
    plot_bgcolor='#FAF8F5',
    paper_bgcolor='#FAF8F5'
)
```

### 4. 时序折线图（如有时序数据）

```python
fig = go.Figure()

fig.add_trace(go.Scatter(
    x=df['date'],
    y=df['value'],
    mode='lines+markers',
    line=dict(color='#E07A5F', width=3),
    marker=dict(size=8, color='#FAF8F5', line=dict(color='#E07A5F', width=2))
))

fig.update_layout(
    title='趋势变化',
    plot_bgcolor='#FAF8F5',
    paper_bgcolor='#FAF8F5',
    xaxis=dict(showgrid=False),
    yaxis=dict(showgrid=True, gridcolor='#E8E6E3')
)
```

## 截图友好设计

### 单图规范

```css
.chart-container {
    width: 1200px;        /* 高清输出 */
    padding: 40px;
    background: #FAF8F5;
    border-radius: 8px;
}

/* 确保文字清晰 */
.tick text {
    font-size: 14px;
    fill: #2C3E50;
}

/* 对比度 */
.marker {
    stroke: #3D405B;      /* 深色描边 */
    stroke-width: 1;
}
```

### 多图布局

```html
<div class="dashboard">
    <!-- 第一行：KPI 卡片 -->
    <div class="row">
        <div class="kpi-card">...</div>
        <div class="kpi-card">...</div>
        <div class="kpi-card">...</div>
    </div>

    <!-- 第二行：核心图表 -->
    <div class="row">
        <div class="chart-main">...</div>
    </div>

    <!-- 第三行：辅助图表 -->
    <div class="row">
        <div class="chart-half">...</div>
        <div class="chart-half">...</div>
    </div>
</div>
```

## 完整 HTML 模板

```html
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            background: #FAF8F5;
            font-family: system-ui, -apple-system, sans-serif;
            color: #2C3E50;
            padding: 40px;
        }
        .header {
            text-align: center;
            margin-bottom: 40px;
        }
        .header h1 {
            color: #3D405B;
            font-size: 32px;
            font-weight: 700;
        }
        .header p {
            color: #2C3E50;
            font-size: 14px;
            margin-top: 8px;
        }
        .chart-container {
            background: white;
            border-radius: 12px;
            padding: 30px;
            margin-bottom: 30px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.04);
        }
        .kpi-grid {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 24px;
            margin-bottom: 30px;
        }
        .kpi-card {
            background: white;
            border-radius: 12px;
            padding: 24px;
            text-align: center;
            box-shadow: 0 2px 8px rgba(0,0,0,0.04);
        }
        .kpi-value {
            font-size: 36px;
            font-weight: 700;
            color: #E07A5F;
        }
        .kpi-label {
            font-size: 13px;
            color: #2C3E50;
            margin-top: 8px;
        }
        .footer {
            text-align: center;
            font-size: 12px;
            color: #999;
            margin-top: 40px;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>分析报告标题</h1>
        <p>数据来源：XXX | 分析时间：202X年X月</p>
    </div>

    <div class="kpi-grid">
        <div class="kpi-card">
            <div class="kpi-value">0.39</div>
            <div class="kpi-label">核心相关系数</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-value">346</div>
            <div class="kpi-label">分析职业数</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-value">1.47亿</div>
            <div class="kpi-label">受影响就业人数</div>
        </div>
    </div>

    <div class="chart-container">
        <div id="main-chart"></div>
    </div>

    <div class="footer">
        由 Vibe Analysis 生成 | 使用 Claude Code 辅助分析
    </div>

    <script>
        // Plotly 图表配置
        var trace1 = {
            x: [/* 数据 */],
            y: [/* 数据 */],
            mode: 'markers',
            marker: {
                color: '#81B29A',
                size: 12,
                line: {color: '#3D405B', width: 1}
            }
        };

        var layout = {
            title: {text: '核心发现', font: {size: 18, color: '#3D405B'}},
            paper_bgcolor: 'white',
            plot_bgcolor: 'white',
            font: {family: 'system-ui', color: '#2C3E50'}
        };

        Plotly.newPlot('main-chart', [trace1], layout);
    </script>
</body>
</html>
```

## 实现路径选择

| 工具 | 适用场景 | 优点 | 缺点 |
|------|---------|------|------|
| Plotly | 交互式看板 | 功能全、可交互 | 文件较大 |
| ECharts | 静态截图 | 体积小、渲染快 | 配置较复杂 |
| Matplotlib | 快速出图 | Python原生 | 样式需调整 |
| HTML+CSS | 定制需求 | 完全可控 | 开发成本高 |

**推荐**：
- 快速迭代：Plotly
- 最终交付：HTML+CSS 定制模板

## 禁止事项

- 不使用冷色调：禁用蓝紫冷色系
- 不过度装饰：禁用阴影、渐变背景、3D效果
- 不拥挤排版：图表间留白 ≥ 30px
- 不小字体：最小字号 11px
