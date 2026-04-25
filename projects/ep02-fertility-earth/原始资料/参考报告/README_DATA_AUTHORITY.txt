全球人口与经济数据集 — 三表关系模型
===============================================================
生成时间: 2026-04-23
数据采集: Hermes Agent 自动化采集

数据模型
--------
星型模型：两个维度表(dim) + 一个关联桥接表(bridge)
- dim_country: 国家维度实体表，精度到"国家-年份"
- dim_city: 城市维度实体表，精度到"城市"
- bridge_country_city: 国家-城市关联关系表 + 占比分析

数据来源权威性说明
------------------

1. World Bank Open Data API
   - 机构: 世界银行 (The World Bank)
   - 地位: 国际最权威的发展统计数据来源
   - 更新频率: 年度，最新数据更新至2026年4月
   - 覆盖范围: 全球213个主权国家/地区
   - 采集方式: REST API (api.worldbank.org/v2)
   - 指标列表:
     * SP.POP.TOTL - 总人口
     * SP.DYN.CBRT.IN - 粗出生率(‰)
     * SP.DYN.CDRT.IN - 粗死亡率(‰)
     * SP.POP.GROW - 人口年增长率(%)
     * SP.DYN.TFRT.IN - 总和生育率
     * SP.DYN.LE00.IN - 出生时预期寿命(年)
     * SP.URB.TOTL.IN.ZS - 城市人口占比(%)
     * SP.DYN.IMRT.IN - 婴儿死亡率(‰)
     * NY.GDP.MKTP.CD - GDP(当年价格美元)
     * NY.GDP.PCAP.CD - 人均GDP(美元)
     * NY.GDP.MKTP.KD.ZG - GDP年增长率(%)
     * FP.CPI.TOTL.ZG - 通货膨胀率(%)
     * SL.UEM.TOTL.ZS - 失业率(%)
     * TG.VAL.TOTL.GD.ZS - 贸易占GDP比重(%)

2. citypopulation.de (Thomas Brinkhoff)
   - 机构: 独立人口统计研究网站，由德国学者 Thomas Brinkhoff 维护
   - 地位: 国际知名的城市人口统计专业网站
   - 原始数据来源: 各国官方统计机构、人口普查、UN DESA
   - 更新频率: 不定期，城市群数据参考日期为2026-01-01
   - 补充字段:
     * 出生率、死亡率、预期寿命、生育率
     * 城市化率、中位年龄、人口增长率
     * 城市群人口、面积、增长率、类型标记

数据质量标记说明
------------------
Data_Quality_Flag 字段含义:
- Complete: 14个WB指标全部有值
- Good: 10-13个指标有值
- Partial: 5-9个指标有值
- Sparse: 少于5个指标有值

国家名称映射说明
------------------
citypopulation.de 与 World Bank 的国家命名存在差异，bridge表已做手动映射修正：
- United States of America → United States
- Korea (South) → Korea, Rep.
- Russia → Russian Federation
- Vietnam → Viet Nam
- Iran → Iran, Islamic Rep.
- 等(详见bridge表生成逻辑)

关联分析建议
------------------
1. 人口-经济联合分析
   SQL: SELECT c.*, b.City_Population, b.City_Share_of_Country_pct
        FROM dim_country c
        JOIN bridge_country_city b ON c.Country = b.Country
        WHERE c.Year = '2024'

2. 城市化水平分析
   SQL: SELECT Country, Urbanization_pct, GDP_per_Capita_USD
        FROM dim_country WHERE Year = '2024'

3. 城市群集中度分析
   SQL: SELECT Country, SUM(City_Population) as total_agglo_pop,
               MAX(City_Share_of_Country_pct) as max_share
        FROM bridge_country_city
        GROUP BY Country

数据局限性
--------
1. 城市数据: 仅包含人口≥1000万的主要城市群(157个)，未覆盖所有城市
2. 城市历史数据: CP数据为最新参考值(2026-01-01)，无完整10年历史序列
3. 缺失值: 部分国家/年份某些指标缺失(尤其是2024年预估数据)
4. 统计口径: WB与CP的统计方法存在差异，建议交叉验证


更新: 区域历史人口数据 (dim_region_history.csv)
-----------------------------------------------------------
时间: 2026-04-23
覆盖: 2597行, 20个国家/地区

国家覆盖:
- 东亚: 中国(31省/5轮普查) 、日本(48县/7轮) 、韩国(13道/6轮) 、越南(63省/3轮)
  泰国(7区) 、印度尼西亚(30省/5轮) 、菲律宾(4大区) 、马来西亚(16州)
  台湾(22县市/5轮)
- 美国: 51州/领地 (1990/2000/2010/2020普查 + 2024年度估计)
- 欧洲: 德国(17州) 、法国(14大区/7轮) 、意大利(21大区/6轮)
  西班牙(20自治区) 、英国(5区) 、俄罗斯(9联邦区)
  荷兰(13省) 、瑞典(22省/8轮) 、波兰(17省) 、土耳其(81省/5轮)

区域命名说明:
- 美国: 使用州代码 (CA=加州, NY=纽约, TX=德克萨斯)
- 日本: 使用都道府县代码 (13=东京都, 27=大阪府, 01=北海道)
- 其他国家: 使用正式英文名称

格式: 长表(Long format) - 每行 = Country + Region + Date + Population
用途: 跨国区域人口增长对比、城市化演变、人口流动分析

示例数据:
- 广东省: 1982年5930万 → 2020年1.26亿 (增长113%)
- 加州(CA): 1990年2976万 → 2024年3943万 (增长33%)
- 东京都(13): 1995年1177万 → 2024年1418万 (增长20%)
- 首尔(Seoul): 1980年836万 → 2020年959万 (增长15%，2010后持续减少)
