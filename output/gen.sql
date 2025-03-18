SELECT
    h.highway_code AS '路线编码',
    hs.simple_name AS '路段简称',
    e.direction AS '行车方向',
    e.roadway AS '车道',
    mu.management_unit_name AS '管理中心',
    e.check_year AS '检测时间',
    e.data_source AS '数据来源',
    e.evaluation_unit AS '评价单元',
    e.start_pile_code AS '起点桩号',
    e.end_pile_code AS '终点桩号',
    AVG(e.pqi) AS 'PQI均值',
    AVG(e.pci) AS 'PCI均值',
    AVG(e.rdi) AS 'RDI均值',
    AVG(e.rqi) AS 'RQI均值',
    AVG(e.pbi) AS 'PBI均值',
    AVG(e.pwi) AS 'PWI均值',
    -- 假设衰变值、提升值、变化趋势是通过某种计算得出的
    -- 这里仅作为示例，具体计算需要根据业务逻辑定义
    (MAX(e.pqi) - MIN(e.pqi)) AS 'PQI衰变值',
    (MAX(e.pci) - MIN(e.pci)) AS 'PCI衰变值',
    (MAX(e.rdi) - MIN(e.rdi)) AS 'RDI衰变值',
    (MAX(e.rqi) - MIN(e.rqi)) AS 'RQI衰变值'
FROM 
    evaluation_0227_to_li e
JOIN 
    highway_segment_0227_to_li hs ON e.highway_segment_id = hs.id
JOIN 
    highway_0227_to_li h ON hs.highway_id = h.id
JOIN 
    management_unit_0227_to_li mu ON e.management_unit_id = mu.id
WHERE 
    e.start_pile_code >= 0 AND e.end_pile_code <= 100
GROUP BY 
    h.highway_code, hs.simple_name, e.direction, e.roadway, mu.management_unit_name, e.check_year, e.data_source, e.evaluation_unit