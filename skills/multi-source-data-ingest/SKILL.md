---
name: multi-source-data-ingest
description: "多源异构数据标准化入库流程。关键词：数据入库、多源数据、数据整合、SQLite、职业代码映射、数据标准化"
metadata:
  type: tool
  version: 1.0.0
---

# 多源数据入库

异构数据标准化进 SQLite 的完整流程。

## 触发条件

- 需要整合多个数据源（PDF/Excel/CSV）
- 需要建立统一的分析数据库
- 需要处理职业代码映射等跨数据源关联

## 标准建表结构

```sql
-- 1. 职业基础信息表
CREATE TABLE occupation_base (
    occupation_id TEXT PRIMARY KEY,     -- 统一职业编码
    occupation_name TEXT NOT NULL,       -- 职业名称
    occupation_name_en TEXT,             -- 英文名称（如有）
    major_category TEXT,                 -- 大类
    minor_category TEXT,                 -- 中类
    employment_size INTEGER,             -- 就业人数
    data_source TEXT,                    -- 来源标识
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. AI 暴露度数据
CREATE TABLE ai_exposure (
    occupation_id TEXT PRIMARY KEY,
    ai_exposure_score REAL,              -- AI 暴露度得分 (0-1)
    ai_exposure_rank INTEGER,            -- 排名
    task_automation_potential REAL,      -- 任务自动化潜力
    data_source TEXT,                    -- 来源：PKU/Anthropic/etc
    confidence_level TEXT,               -- 可信度：high/medium/low
    year INTEGER,                        -- 数据年份
    FOREIGN KEY (occupation_id) REFERENCES occupation_base(occupation_id)
);

-- 3. 薪资数据
CREATE TABLE wage_data (
    occupation_id TEXT,
    year INTEGER,
    p10 REAL,                            -- 10分位数
    p25 REAL,                            -- 25分位数
    p50 REAL,                            -- 50分位数（中位数）
    p75 REAL,                            -- 75分位数
    p90 REAL,                            -- 90分位数
    mean REAL,                           -- 平均数
    sample_size INTEGER,                 -- 样本量
    data_source TEXT,                    -- 来源：年鉴/平台报告
    PRIMARY KEY (occupation_id, year),
    FOREIGN KEY (occupation_id) REFERENCES occupation_base(occupation_id)
);

-- 4. 平台趋势数据（招聘平台报告）
CREATE TABLE platform_trend (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    platform_name TEXT,                  -- 猎聘/智联/脉脉
    metric_name TEXT,                    -- 指标名：薪资增速/供需比
    metric_value REAL,
    unit TEXT,                           -- 单位：%/元/比例
    year INTEGER,
    quarter INTEGER,
    confidence_level TEXT DEFAULT 'medium', -- 平台数据默认中可信度
    notes TEXT                           -- 备注
);
```

## 职业代码统一套路

### O*NET → 中国职业分类映射

```python
# 1. 建立映射表
CREATE TABLE occupation_mapping (
    onet_soc_code TEXT,                  -- O*NET 编码
    cocc_code TEXT,                      -- 中国职业编码
    mapping_method TEXT,                 -- 方法：keyword/ai/manual
    confidence_score REAL,               -- 置信度 0-1
    match_reason TEXT                    -- 匹配理由
);

# 2. 三步映射策略
# Step 1: 关键词匹配（职业名称相似度）
# Step 2: AI 辅助匹配（LLM 判断语义相似性）
# Step 3: 人工校正（记录未匹配和存疑项）
```

### 映射规则

| 场景 | 处理方式 |
|------|---------|
| 一对一 | 直接映射，confidence=1.0 |
| 一对多 | 拆分为多条记录，标注"拆分映射" |
| 多对一 | 取平均值或加权平均，标注"合并映射" |
| 无匹配 | 记录到 `unmatched_occupations` 表，人工处理 |

## 数据分层入库策略

### 可信度标注

```sql
-- 官方统计数据
UPDATE table_name SET confidence_level = 'high'
WHERE data_source IN ('国家统计局', 'BLS', '官方年鉴');

-- 学术研究机构
UPDATE table_name SET confidence_level = 'high'
WHERE data_source IN ('Anthropic', '北大', 'Stanford');

-- 招聘平台报告
UPDATE table_name SET confidence_level = 'medium'
WHERE data_source IN ('猎聘', '智联', '脉脉');

-- 估算/模型预测
UPDATE table_name SET confidence_level = 'low'
WHERE data_source LIKE '%estimate%' OR data_source LIKE '%model%';
```

### 分层查询示例

```sql
-- 高可信度优先查询
SELECT * FROM wage_data
WHERE occupation_id = 'X'
ORDER BY
    CASE confidence_level
        WHEN 'high' THEN 1
        WHEN 'medium' THEN 2
        WHEN 'low' THEN 3
    END,
    year DESC;
```

## PDF 报告手动提取规范

### 提取模板

```markdown
# 数据提取记录

## 来源
- 文件: [文件名]
- 页码: [页码范围]
- 提取日期: [日期]
- 提取人: [姓名]

## 提取内容

| 字段 | 值 | 单位 | 备注 |
|------|-----|------|------|
| | | | |

## 原始截图
[保存截图路径]

## 置信度评估
- 数据清晰度: [高/中/低]
- 理解确定性: [高/中/低]
- 备注: [任何存疑点]
```

### 提取原则

1. **保留原始格式**：截图存档，方便复核
2. **标注页码**：每个数据点必须可溯源
3. **记录近似值**：如果图表只能估算，标注"目测估计±X%"

## 入库检查清单

- [ ] 所有源文件已读取并记录路径
- [ ] 主键冲突已处理（更新/跳过/合并）
- [ ] 外键约束已验证
- [ ] 数据类型已校验（无字符串混入数字列）
- [ ] 编码统一（UTF-8）
- [ ] 可信度字段已填充
- [ ] 未匹配项已记录到 `unmatched_occupations`

## 执行流程

1. **读取源文件** → 使用 pandas/excel-reader 读取
2. **字段映射** → 将原始字段名映射到标准字段名
3. **数据清洗** → 处理缺失值、异常值、格式统一
4. **代码映射** → 执行职业代码映射
5. **分层入库** → 按可信度标注插入数据库
6. **质量校验** → 调用 data-quality-check 验证

## 禁止事项

- 不删除原始数据：保留原始文件，只做增量更新
- 不覆盖高可信数据：低可信数据不覆盖高可信数据
- 不忽略未匹配项：必须记录并追踪未匹配的职业代码
