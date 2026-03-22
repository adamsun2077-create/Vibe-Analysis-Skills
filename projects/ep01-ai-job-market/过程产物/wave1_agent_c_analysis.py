#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Wave 1 Agent C: 中美职业暴露指数重叠分析
目标：确定 H2（中美排名对比）的可用样本
"""

import pandas as pd
import numpy as np

# ============================================================
# Step 1: 加载数据，检查 SOC 代码格式
# ============================================================

print("=" * 60)
print("Step 1: 加载数据")
print("=" * 60)

# 加载中国暴露指数（SOC细分层）
china_path = "/Users/adam/Aidam_3/data-analysis/ai-job-market-analysis/原始资料/核心数据/人工智能-大语言模型技术\"暴露指数数据/exposure_base_soc_detail.xlsx"
anthropic_path = "/Users/adam/Aidam_3/data-analysis/ai-job-market-analysis/原始资料/核心数据/anthropic-job-exposure.csv"

china_df = pd.read_excel(china_path)
anthropic_df = pd.read_csv(anthropic_path)

print(f"\n中国数据：{len(china_df)} 行")
print(f"中国数据列名：{list(china_df.columns)}")
print(f"\nAnthropic数据：{len(anthropic_df)} 行")
print(f"Anthropic数据列名：{list(anthropic_df.columns)}")

print("\n--- 中国数据前5行 ---")
print(china_df.head())

print("\n--- Anthropic数据前5行 ---")
print(anthropic_df.head())

# 检查 SOC 代码格式
print("\n--- SOC 代码格式样例 ---")
print(f"中国 occu_soc_code 样例：{china_df['occu_soc_code'].head(5).tolist()}")
print(f"Anthropic occ_code 样例：{anthropic_df['occ_code'].head(5).tolist()}")

print(f"\n中国 SOC 代码类型：{china_df['occu_soc_code'].dtype}")
print(f"Anthropic SOC 代码类型：{anthropic_df['occ_code'].dtype}")

# ============================================================
# SOC 代码标准化逻辑
# ============================================================
# 标准化规则：取前7位（格式 XX-XXXX，即含连字符共7位）
# 中国数据：11-1011.00 → 11-1011
# Anthropic数据：11-1011 → 11-1011（本已是7位，保持不变）

def normalize_soc(code):
    """标准化SOC代码：统一取前7位（XX-XXXX格式）"""
    code_str = str(code).strip()
    # 去除小数点及后续内容（如 .00）
    if '.' in code_str:
        code_str = code_str.split('.')[0]
    # 取前7位（含连字符）
    return code_str[:7]

china_df['soc_normalized'] = china_df['occu_soc_code'].apply(normalize_soc)
anthropic_df['soc_normalized'] = anthropic_df['occ_code'].apply(normalize_soc)

print("\n--- 标准化后 SOC 代码样例 ---")
print(f"中国（标准化后）：{china_df['soc_normalized'].head(5).tolist()}")
print(f"Anthropic（标准化后）：{anthropic_df['soc_normalized'].head(5).tolist()}")

# 检查标准化后格式一致性
print(f"\n中国 SOC 代码长度分布：\n{china_df['soc_normalized'].str.len().value_counts()}")
print(f"\nAnthropic SOC 代码长度分布：\n{anthropic_df['soc_normalized'].str.len().value_counts()}")

# ============================================================
# Step 2: 计算重叠
# ============================================================

print("\n" + "=" * 60)
print("Step 2: 计算重叠")
print("=" * 60)

china_soc_set = set(china_df['soc_normalized'])
anthropic_soc_set = set(anthropic_df['soc_normalized'])

overlap_set = china_soc_set & anthropic_soc_set
only_china_set = china_soc_set - anthropic_soc_set
only_anthropic_set = anthropic_soc_set - china_soc_set

print(f"\n重叠职业数（精确匹配）：{len(overlap_set)}")
print(f"仅中国有：{len(only_china_set)}")
print(f"仅Anthropic有：{len(only_anthropic_set)}")

# 合并重叠职业
overlap_china = china_df[china_df['soc_normalized'].isin(overlap_set)][['soc_normalized', 'occu_soc_code', 'onet_occupationtitle', 'exposure']].copy()
overlap_china.columns = ['soc_normalized', 'china_soc_raw', 'onet_title', 'china_exposure']

overlap_anthropic = anthropic_df[anthropic_df['soc_normalized'].isin(overlap_set)][['soc_normalized', 'occ_code', 'title', 'observed_exposure']].copy()
overlap_anthropic.columns = ['soc_normalized', 'anthropic_soc_raw', 'anthropic_title', 'anthropic_exposure']

# 合并
overlap_df = overlap_china.merge(overlap_anthropic, on='soc_normalized', how='inner')

print(f"\n合并后重叠职业数：{len(overlap_df)}")
print("\n--- 完整重叠职业列表 ---")
print(overlap_df[['soc_normalized', 'onet_title', 'china_exposure', 'anthropic_exposure']].to_string(index=False))

# ============================================================
# Step 3: 初步排名对比
# ============================================================

print("\n" + "=" * 60)
print("Step 3: 排名对比")
print("=" * 60)

# 在各自完整数据集中计算排名（从高到低，rank=1为最高暴露度）
china_df['china_rank_all'] = china_df['exposure'].rank(ascending=False, method='min').astype(int)
anthropic_df['anthropic_rank_all'] = anthropic_df['observed_exposure'].rank(ascending=False, method='min').astype(int)

# 将排名合并进重叠数据集
overlap_df = overlap_df.merge(
    china_df[['soc_normalized', 'china_rank_all']],
    on='soc_normalized', how='left'
)
overlap_df = overlap_df.merge(
    anthropic_df[['soc_normalized', 'anthropic_rank_all']],
    on='soc_normalized', how='left'
)

# 计算排名差值：中国排名 - Anthropic排名
# 正值：中国排名比Anthropic靠后（中国暴露度相对偏低）
# 负值：中国排名比Anthropic靠前（中国暴露度相对偏高）
overlap_df['delta_rank'] = overlap_df['china_rank_all'] - overlap_df['anthropic_rank_all']

print(f"\n排名差值（Δrank = 中国排名 - Anthropic排名）统计：")
print(overlap_df['delta_rank'].describe())

# Top 10 排名差异最大的职业（绝对值）
top10_diff = overlap_df.reindex(overlap_df['delta_rank'].abs().nlargest(10).index)
print("\n--- 排名差异 Top 10（绝对值最大）---")
print(top10_diff[['soc_normalized', 'onet_title', 'china_rank_all', 'anthropic_rank_all', 'delta_rank', 'china_exposure', 'anthropic_exposure']].to_string(index=False))

# 中国相对高的 Top 5（Δrank 最负，即中国排名数字小，暴露度相对更高）
top5_china_higher = overlap_df.nsmallest(5, 'delta_rank')
print("\n--- 中国排名显著高于全球 Top 5（Δrank 最负）---")
print(top5_china_higher[['soc_normalized', 'onet_title', 'china_rank_all', 'anthropic_rank_all', 'delta_rank']].to_string(index=False))

# 中国相对低的 Top 5（Δrank 最正，即中国排名数字大，暴露度相对更低）
top5_china_lower = overlap_df.nlargest(5, 'delta_rank')
print("\n--- 中国排名显著低于全球 Top 5（Δrank 最正）---")
print(top5_china_lower[['soc_normalized', 'onet_title', 'china_rank_all', 'anthropic_rank_all', 'delta_rank']].to_string(index=False))

# ============================================================
# Step 4: 按职业大类汇总
# ============================================================

print("\n" + "=" * 60)
print("Step 4: 按职业大类汇总")
print("=" * 60)

# 提取 SOC Major Group（前2位）
overlap_df['major_group'] = overlap_df['soc_normalized'].str[:2]

# SOC 大类名称映射
major_group_names = {
    '11': '管理类（Management）',
    '13': '商业和金融类（Business & Financial）',
    '15': '计算机和数学类（Computer & Mathematical）',
    '17': '建筑和工程类（Architecture & Engineering）',
    '19': '生命、物理和社会科学类（Life, Physical & Social Science）',
    '21': '社区和社会服务类（Community & Social Service）',
    '23': '法律类（Legal）',
    '25': '教育、培训和图书馆类（Educational Instruction & Library）',
    '27': '艺术、设计、娱乐、体育和媒体类（Arts, Design, Entertainment）',
    '29': '医疗保健从业人员类（Healthcare Practitioners）',
    '31': '医疗保健支持类（Healthcare Support）',
    '33': '防护服务类（Protective Service）',
    '35': '餐饮和饮食准备类（Food Preparation & Serving）',
    '37': '楼宇和场地清洁与维护类（Building & Grounds Cleaning）',
    '39': '个人护理和服务类（Personal Care & Service）',
    '41': '销售和相关类（Sales & Related）',
    '43': '办公室和行政支持类（Office & Administrative Support）',
    '45': '农业、渔业和林业类（Farming, Fishing & Forestry）',
    '47': '建筑和采矿类（Construction & Extraction）',
    '49': '安装、维护和修理类（Installation, Maintenance & Repair）',
    '51': '生产类（Production）',
    '53': '运输和物料搬运类（Transportation & Material Moving）',
}

overlap_df['major_group_name'] = overlap_df['major_group'].map(major_group_names).fillna(overlap_df['major_group'])

major_summary = overlap_df.groupby(['major_group', 'major_group_name']).agg(
    职业数=('soc_normalized', 'count'),
    平均Δrank=('delta_rank', 'mean'),
    中位Δrank=('delta_rank', 'median'),
    平均中国排名=('china_rank_all', 'mean'),
    平均Anthropic排名=('anthropic_rank_all', 'mean'),
).reset_index().sort_values('平均Δrank')

print("\n--- 各职业大类排名差异汇总（Δrank = 中国排名 - Anthropic排名）---")
print("（负值 = 中国系统性偏高；正值 = 中国系统性偏低）")
print(major_summary.to_string(index=False))

# ============================================================
# 收集所有输出供报告使用
# ============================================================

results = {
    'china_total': len(china_df),
    'anthropic_total': len(anthropic_df),
    'overlap_count': len(overlap_df),
    'only_china': len(only_china_set),
    'only_anthropic': len(only_anthropic_set),
    'overlap_df': overlap_df,
    'top10_diff': top10_diff,
    'top5_china_higher': top5_china_higher,
    'top5_china_lower': top5_china_lower,
    'major_summary': major_summary,
}

print("\n\n=== 分析完成，准备写入报告 ===")

# 保存中间结果
overlap_df.to_csv('/Users/adam/Aidam_3/data-analysis/ai-job-market-analysis/wave1_agent_c_overlap.csv', index=False, encoding='utf-8-sig')
print("已保存重叠数据到 wave1_agent_c_overlap.csv")
