---
name: data-quality-check
description: "数据质量验证清单。关键词：数据校验、质量检查、数据清洗、缺失率检查、极值检查、数据质量报告"
metadata:
  type: process
  version: 1.0.0
---

# 数据质量校核

分析开始前必做的质量验证清单。

## 触发条件

- 数据刚入库或加载完成
- 开始任何分析前
- 发现异常结果需要回溯数据问题时

## 四项必查

### 1. 记录数检查

```python
# 检查清单
- [ ] 各表记录数符合预期
- [ ] 主表与明细表记录数匹配
- [ ] 时间序列数据无断档

# SQL 示例
SELECT
    'occupation_base' as table_name, COUNT(*) as cnt FROM occupation_base
UNION ALL
SELECT 'ai_exposure', COUNT(*) FROM ai_exposure
UNION ALL
SELECT 'wage_data', COUNT(*) FROM wage_data;
```

### 2. 字段缺失率检查

```python
# 标准：关键字段缺失率 < 5%，非关键字段 < 20%

# SQL 示例
SELECT
    'ai_exposure_score' as field,
    COUNT(*) as total,
    COUNT(CASE WHEN ai_exposure_score IS NULL THEN 1 END) as null_count,
    ROUND(100.0 * COUNT(CASE WHEN ai_exposure_score IS NULL THEN 1 END) / COUNT(*), 2) as null_pct
FROM ai_exposure;
```

**处理规则**：
- 缺失率 < 5%：可接受
- 缺失率 5-20%：标注并检查是否系统性缺失
- 缺失率 > 20%：该字段暂不纳入主要结论

### 3. 代码格式一致性检查

```python
# 检查职业代码格式统一
# 示例：中国职业代码应为 6 位数字

SELECT occupation_id, occupation_name
FROM occupation_base
WHERE occupation_id NOT REGEXP '^[0-9]{6}$';
```

**常见格式问题**：
- 前后空格
- 大小写不一致
- 分隔符差异（- vs _）
- 编码问题（中文标点）

### 4. 极值合理性检查

```python
# 检查数值是否在合理范围内

SELECT
    MIN(ai_exposure_score) as min_score,
    MAX(ai_exposure_score) as max_score,
    AVG(ai_exposure_score) as avg_score,
    MIN(p50) as min_wage,
    MAX(p50) as max_wage
FROM ai_exposure a
JOIN wage_data w ON a.occupation_id = w.occupation_id;

# 合理性判断
# - AI暴露度应在 0-1 之间
# - 薪资中位数应在合理区间（如 3000-500000）
```

## 加权均值陷阱

### 问题描述

小职业的数据点可能扭曲总体结论。

```
示例：
- 职业A：就业人数100万，薪资5000，AI暴露度0.9
- 职业B：就业人数1000人，薪资20000，AI暴露度0.9

错误做法：简单平均 → 两个职业都是0.9
正确做法：加权平均 → 以就业人数为权重
```

### 识别方法

```python
# 检查就业人数分布
SELECT
    CASE
        WHEN employment_size < 1000 THEN '小型(<1k)'
        WHEN employment_size < 10000 THEN '中型(1k-10k)'
        WHEN employment_size < 100000 THEN '大型(10k-100k)'
        ELSE '超大型(>100k)'
    END as size_category,
    COUNT(*) as occupation_count,
    SUM(employment_size) as total_employment
FROM occupation_base
GROUP BY size_category;
```

### 处理策略

```python
# 策略1：就业人数加权
weighted_avg = sum(value * employment_size) / sum(employment_size)

# 策略2：分层分析
# 大型职业单独分析，小型职业归类分析

# 策略3：标注样本量
# 每个统计结果标注 n=（有效样本数）
```

## 关联校验

### 职业代码匹配率检查

```python
# 检查映射完整性

SELECT
    data_source,
    COUNT(*) as total_records,
    COUNT(CASE WHEN occupation_id IN (SELECT occupation_id FROM occupation_base) THEN 1 END) as matched,
    ROUND(100.0 * COUNT(CASE WHEN occupation_id IN (SELECT occupation_id FROM occupation_base) THEN 1 END) / COUNT(*), 1) as match_rate
FROM ai_exposure
GROUP BY data_source;
```

**预期标准**：
- 同源数据匹配率 > 90%
- 跨源映射匹配率 60-70%（需人工复核）

### 未匹配项记录

```sql
CREATE TABLE unmatched_occupations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_table TEXT,
    source_id TEXT,
    source_name TEXT,
    reason TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 插入未匹配记录
INSERT INTO unmatched_occupations (source_table, source_id, source_name, reason)
SELECT 'ai_exposure', occupation_id, NULL, 'No matching occupation_base record'
FROM ai_exposure
WHERE occupation_id NOT IN (SELECT occupation_id FROM occupation_base);
```

## 数据质量报告模板

```markdown
# 数据质量报告

**检查时间**: 202X-XX-XX
**检查人**: [姓名]
**数据版本**: [版本标识]

## 1. 记录数检查

| 表名 | 预期记录数 | 实际记录数 | 状态 |
|------|-----------|-----------|------|
| | | | ✅/⚠️/❌ |

## 2. 缺失率检查

| 字段 | 缺失数 | 缺失率 | 阈值 | 状态 |
|------|-------|-------|------|------|
| | | | | |

## 3. 极值检查

| 字段 | 最小值 | 最大值 | 合理范围 | 异常数 |
|------|-------|-------|---------|-------|
| | | | | |

## 4. 关联检查

| 数据源 | 记录数 | 匹配数 | 匹配率 | 预期 | 状态 |
|--------|-------|-------|-------|------|------|
| | | | | | |

## 5. 未匹配项

[列出需要人工处理的关键未匹配项]

## 6. 质量评估结论

- [ ] 数据质量满足分析要求
- [ ] 需要处理的问题已标注
- [ ] 分析范围已根据数据质量调整

**下一步**: [进入分析 / 先处理数据问题]
```

## 执行流程

1. **运行四项必查** → 生成基础统计
2. **检查加权陷阱** → 确认是否需要加权处理
3. **验证关联匹配** → 记录未匹配项
4. **生成质量报告** → 使用模板输出 markdown
5. **确认分析范围** → 根据质量调整后续分析策略

## 禁止事项

- 不忽略高缺失率：缺失率>20%的字段必须标注
- 不假设匹配成功：必须显式检查匹配率
- 不掩盖数据问题：所有异常必须记录并说明影响
