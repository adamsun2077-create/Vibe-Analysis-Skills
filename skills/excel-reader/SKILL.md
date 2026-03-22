---
name: excel-reader
description: "Excel/CSV读取分析。关键词：excel、csv、数据分析"
---

# Excel Reader

## 触发条件

**由 Data Analyst 模式触发:**
- 用户上传 Excel/CSV 文件需要分析
- 分析师需要提取数据进行深度分析
- 多 sheet 数据整合场景

**由用户直接触发（场景较少）:**
- "帮我读取这个 Excel 文件"
- "查看一下 CSV 内容"
- "把 Excel 转换成 JSON"

## 核心功能

### 1. 读取文件

使用 pandas 读取 Excel 文件：

```python
import pandas as pd

# 读取整个文件（所有 sheet）
xl = pd.ExcelFile('文件路径.xlsx')
sheet_names = xl.sheet_names  # 获取所有 sheet 名称

# 读取特定 sheet
df = pd.read_excel('文件路径.xlsx', sheet_name='Sheet1')
# 或按索引
df = pd.read_excel('文件路径.xlsx', sheet_name=0)
```

### 2. 基本数据查看

```python
# 查看基本信息
print(f"行数: {len(df)}, 列数: {len(df.columns)}")
print(f"列名: {list(df.columns)}")

# 查看前几行
df.head(10)

# 查看数据类型和统计信息
df.info()
df.describe()
```

### 3. 数据筛选和处理

```python
# 筛选特定列
df[['列名1', '列名2']]

# 条件筛选
df[df['列名'] > 100]
df[df['列名'].str.contains('关键词', na=False)]

# 查找空值
df.isnull().sum()
```

### 4. 格式转换

```python
# 转换为 JSON
json_data = df.to_json(orient='records', force_ascii=False)

# 转换为 CSV
csv_data = df.to_csv(index=False, encoding='utf-8')

# 转换为字典列表
dict_list = df.to_dict('records')
```

## 使用流程

### 步骤 1: 确认需求

询问用户：
- 文件路径
- 需要读取哪个 sheet（如果有多个）
- 具体需求：查看内容、统计数据、筛选特定数据、还是格式转换？

### 步骤 2: 读取和分析

根据需求执行相应操作，使用 `scripts/excel_reader.py` 脚本可以更高效地处理。

### 步骤 3: 结果呈现

- 提供清晰的表格视图（使用 markdown 表格）
- 对于大数据集，提供摘要和前几行示例
- 说明数据特征（行数、列数、空值情况等）

## 脚本工具

技能包含以下辅助脚本：

- `scripts/excel_reader.py` - 通用 Excel 读取和格式化工具

## 注意事项

1. **文件路径**: 支持绝对路径和相对路径
2. **大文件处理**: 对于超过 10000 行的文件，只显示前 100 行和统计摘要
3. **编码问题**: 自动处理 UTF-8 和 GBK 编码的 CSV 文件
4. **合并单元格**: pandas 会将合并单元格的值填充到所有相关行
5. **日期格式**: 自动识别并转换为标准日期格式

## 示例用法

```
用户: "帮我读取 data.xlsx 文件"
→ 读取文件并显示基本信息和前 10 行

用户: "统计一下 sales.xlsx 中每个类别的总金额"
→ 读取文件，按类别分组，计算总和

用户: "将 data.xlsx 转换为 JSON 格式"
→ 读取 Excel，转换为 JSON，保存或显示
```
