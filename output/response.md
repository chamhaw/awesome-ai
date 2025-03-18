为了实现您描述的功能，我们需要编写一些SQL查询来获取所需的数据。根据您的要求，我们将按照路线、路段、上下行、车道、路公司、管理中心、时间、数据来源、评价单元以及指定的起终点桩号进行统计，并计算各项指标的均值、衰变值、提升值及变化趋势。此外，还需要对各路段的达标率和优等率进行评定。

首先，我们先创建一个基本的查询模板，该模板将从`evaluation_0227_to_li`表中提取数据。这个例子中，我假设您需要统计PQI（路面质量指数）的均值。请根据实际需求调整列名或添加其他指标。

### SQL 查询示例 1: 计算PQI的均值

```sql
SELECT 
    h.simple_name AS '路线简称',
    hs.simple_name AS '路段简称',
    e.direction AS '行车方向',
    e.roadway AS '车道数',
    mu.management_unit_name AS '管养单位名称',
    cu.full_name AS '中心级管理段名称',
    DATE_FORMAT(e.check_year, '%Y') AS '检测年份',
    e.data_source AS '数据来源',
    e.evaluation_unit AS '评价单元',
    MIN(e.start_pile_code) AS '起点桩号编号',
    MAX(e.end_pile_code) AS '终点桩号编号',
    AVG(e.pqi) AS 'PQI均值'
FROM 
    evaluation_0227_to_li e
JOIN 
    highway_segment_0227_to_li hs ON e.highway_segment_id = hs.id
JOIN 
    highway_0227_to_li h ON hs.highway_id = h.id
JOIN 
    management_unit_0227_to_li mu ON e.management_unit_id = mu.id
LEFT JOIN 
    (SELECT * FROM blade_dept_0227_to_li WHERE dept_category = 3) cu ON e.center_segment_id = cu.id
WHERE 
    e.is_deleted = 0 AND
    -- 这里可以加入更多条件以细化查询，例如特定的时间范围、路线、管理单位等
    e.check_year BETWEEN '2020-01-01' AND '2023-12-31' AND
    h.code = 'G0512' AND
    e.start_pile_code >= 100.000 AND e.end_pile_code <= 200.000
GROUP BY 
    h.simple_name, hs.simple_name, e.direction, e.roadway, mu.management_unit_name, cu.full_name, DATE_FORMAT(e.check_year, '%Y'), e.data_source, e.evaluation_unit
ORDER BY 
    h.simple_name, hs.simple_name, e.direction, e.roadway, DATE_FORMAT(e.check_year, '%Y');
```

### SQL 查询示例 2: 计算PQI的衰变值、提升值及变化趋势

对于衰变值、提升值及变化趋势，通常需要比较不同时间段内的数据。这里给出一个简单的例子，展示如何计算两个连续年度之间的PQI变化情况：

```sql
WITH yearly_pqi AS (
    SELECT 
        h.simple_name AS '路线简称',
        hs.simple_name AS '路段简称',
        e.direction AS '行车方向',
        e.roadway AS '车道数',
        mu.management_unit_name AS '管养单位名称',
        cu.full_name AS '中心级管理段名称',
        YEAR(e.check_year) AS '检测年份',
        e.data_source AS '数据来源',
        e.evaluation_unit AS '评价单元',
        AVG(e.pqi) AS 'PQI均值'
    FROM 
        evaluation_0227_to_li e
    JOIN 
        highway_segment_0227_to_li hs ON e.highway_segment_id = hs.id
    JOIN 
        highway_0227_to_li h ON hs.highway_id = h.id
    JOIN 
        management_unit_0227_to_li mu ON e.management_unit_id = mu.id
    LEFT JOIN 
        (SELECT * FROM blade_dept_0227_to_li WHERE dept_category = 3) cu ON e.center_segment_id = cu.id
    WHERE 
        e.is_deleted = 0 AND
        e.check_year BETWEEN '2020-01-01' AND '2023-12-31' AND
        h.code = 'G0512' AND
        e.start_pile_code >= 100.000 AND e.end_pile_code <= 200.000
    GROUP BY 
        h.simple_name, hs.simple_name, e.direction, e.roadway, mu.management_unit_name, cu.full_name, YEAR(e.check_year), e.data_source, e.evaluation_unit
)
SELECT 
    y1.路线简称,
    y1.路段简称,
    y1.行车方向,
    y1.车道数,
    y1.管养单位名称,
    y1.中心级管理段名称,
    y1.检测年份 AS '前一年',
    y2.检测年份 AS '后一年',
    y1.PQI均值 AS '前一年PQI均值',
    y2.PQI均值 AS '后一年PQI均值',
    (y2.PQI均值 - y1.PQI均值) AS '变化值',
    CASE 
        WHEN (y2.PQI均值 - y1.PQI均值) > 0 THEN '提升'
        WHEN (y2.PQI均值 - y1.PQI均值) < 0 THEN '衰减'
        ELSE '不变'
    END AS '变化趋势'
FROM 
    yearly_pqi y1
JOIN 
    yearly_pqi y2 ON y1.路线简称 = y2.路线简称 AND y1.路段简称 = y2.路段简称 AND y1.行车方向 = y2.行车方向 AND y1.车道数 = y2.车道数 AND y1.管养单位名称 = y2.管养单位名称 AND y1.中心级管理段名称 = y2.中心级管理段名称 AND y1.数据来源 = y2.数据来源 AND y1.评价单元 = y2.评价单元 AND y2.检测年份 = y1.检测年份 + 1
ORDER BY 
    y1.路线简称, y1.路段简称, y1.行车方向, y1.车道数, y1.检测年份;
```

这两个查询提供了基础的数据分析功能，您可以在此基础上进一步扩展，比如增加更多的指标计算、更复杂的条件筛选或数据处理逻辑。对于绘制图表的部分，建议使用BI工具如Tableau、Power BI或者Python中的matplotlib、seaborn库来进行可视化。如果需要生成CSV文件，则可以在执行上述查询后，通过数据库客户端导出结果到CSV格式。