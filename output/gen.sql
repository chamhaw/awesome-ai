SELECT
    highway_code AS '路线编码',
    highway_segment_simple_name AS '路段简称',
    direction AS '行车方向',
    roadway AS '车道',
    management_unit_name AS '管理中心',
    check_year AS '检测时间',
    data_source AS '数据来源',
    evaluation_unit AS '评价单元',
    start_pile_code AS '起点桩号编号',
    end_pile_code AS '终点桩号编号',
    AVG(pqi) AS 'PQI均值',
    AVG(pci) AS 'PCI均值',
    AVG(rdi) AS 'RDI均值',
    AVG(rqi) AS 'RQI均值',
    AVG(pbi) AS 'PBI均值',
    AVG(pwi) AS 'PWI均值',
    AVG(sri) AS 'SRI均值',
    AVG(pssi) AS 'PSSI均值',
    -- 假设衰变值、提升值、变化趋势的计算方法为示例
    (MAX(pqi) - MIN(pqi)) AS 'PQI衰变值',
    (MAX(pqi) - MIN(pqi)) / MIN(pqi) * 100 AS 'PQI提升值',
    CASE
        WHEN (MAX(pqi) - MIN(pqi)) > 0 THEN '上升'
        WHEN (MAX(pqi) - MIN(pqi)) < 0 THEN '下降'
        ELSE '稳定'
    END AS 'PQI变化趋势'
FROM
    evaluation_0227_to_li
WHERE
    start_pile_code >= 0 AND end_pile_code <= 100
GROUP BY
    highway_code, highway_segment_simple_name, direction, roadway, management_unit_name, check_year, data_source, evaluation_unit, start_pile_code, end_pile_code
ORDER BY
    'PQI均值' DESC;