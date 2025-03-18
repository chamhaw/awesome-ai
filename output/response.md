为了实现您所描述的需求，我们将构建一个查询来统计各项指标的均值、衰变值、提升值及变化趋势。同时，我们将根据国标评定和省厅评定的要求对各路段的达标率、优等率进行评估，并生成相应的车道级分级分色图。

由于您的需求非常具体且复杂，涉及到多个表之间的关联以及复杂的计算逻辑，我将提供一个基础框架SQL语句，这个框架可以帮助我们开始构建所需的分析功能。请注意，实际应用中可能需要根据具体的业务规则和数据情况进行调整。这里假设我们需要统计`evaluation_0227_to_li`表中的部分关键指标（如PQI, PCI, RDI, RQI等），并基于路线/路段/上下行/车道/路公司/管理中心/时间/数据来源/评价单元/指定起终点桩号等维度进行汇总。

### 基础查询示例
```sql
-- 统计各维度下的平均PQI, PCI, RDI, RQI等
SELECT
    h.code AS highway_code,
    hs.simple_name AS segment_name,
    e.direction,
    e.roadway,
    mu.management_unit_name,
    cu.full_name AS center_segment_name,
    YEAR(e.check_year) AS check_year,
    e.data_source,
    e.evaluation_unit,
    AVG(e.pqi) AS avg_pqi,
    AVG(e.pci) AS avg_pci,
    AVG(e.rdi) AS avg_rdi,
    AVG(e.rqi) AS avg_rqi,
    -- 可以继续添加其他感兴趣的指标
    COUNT(*) AS record_count
FROM
    evaluation_0227_to_li e
JOIN
    highway_segment_0227_to_li hs ON e.highway_segment_id = hs.id
JOIN
    highway_0227_to_li h ON hs.highway_id = h.id
LEFT JOIN
    management_unit_0227_to_li mu ON e.management_unit_id = mu.id
LEFT JOIN
    highway_segment_0227_to_li cu ON e.center_segment_id = cu.id
WHERE
    -- 添加条件过滤，例如：
    -- e.start_pile_code >= 10 AND e.end_pile_code <= 20
    -- e.is_deleted = 0
GROUP BY
    h.code, hs.simple_name, e.direction, e.roadway, mu.management_unit_name, cu.full_name, YEAR(e.check_year), e.data_source, e.evaluation_unit
ORDER BY
    h.code, hs.simple_name, e.direction, e.roadway, check_year;
```

### 注意事项
- 上述查询仅作为起点，实际使用时需考虑更多细节，比如如何处理不同年份间的数据对比以计算衰变值或提升值。
- 对于绘制图表的功能，通常这一步是在应用程序层完成的，通过前端技术（如JavaScript库ECharts, Highcharts）结合后端提供的数据来实现。
- 如果需要进一步细化到特定的起终点桩号范围，可以在`WHERE`子句中加入相应的条件。
- 考虑到性能问题，在处理大数据集时可能需要优化索引设计或采用更高级的数据处理策略。

希望这段代码能够帮助你启动项目！如果有任何具体的定制化需求或其他方面的问题，请随时告知。