### 道路管理系统 RAG 知识库（结构化 SQL 生成版）
```markdown
# 数据表核心维度与关联图谱

## 1. 表结构摘要
| 表名                     | 核心业务意义               | 主键字段       | 关键关联字段                    |
|--------------------------|--------------------------|---------------|--------------------------------|
| `blade_dept_0227_to_li`  | 机构层级树               | `id`          | `parent_id` ↔ 自关联           |
| `highway_0227_to_li`     | 国高网路线元数据         | `id`          | `code`(路线编码)               |
| `highway_segment_0227_to_li` | 物理路段属性         | `id`          | `management_segment_id`(逻辑段) <br> `highway_id`(路线) |
| `evaluation_0227_to_li`  | 路面检测指标数据         | `id`          | `highway_segment_id`(路段) <br> `management_unit_id`(管养单位) |
| `management_unit_0227_to_li` | 管养单位结构       | `id`          | `parent_id` ↔ 自关联           |

## 2. 关键字段语义说明
### 机构表 (`blade_dept_0227_to_li`)
```sql
/* 典型业务标签 */
- dept_category=1 → 集团节点 
- dept_category=2 → 路公司节点 
- ancestors LIKE '100,%' → 属于ID=100的集团下属单位
```

### 定检数据表 (`evaluation_0227_to_li`)
```sql
/* 核心分析维度 */
`data_source`: 
  1-集团检（内部数据） / 2-省检（外部数据）
`direction`: 
  11-上行 / 12-下行 / 20-双向
`pqi_gp`: 
  '优'/'良'/'中'/'次'/'差'（国标评级）
`check_year`: 
  检测时间范围筛选
```

## 3. 多表关联路径
### 路径1：机构→管养单位→路段→检测数据
```sql
d_dept.id (集团ID) 
→ highway_segment.management_unit_id 
→ evaluation.highway_segment_id
```
**适用场景**：统计集团下属所有路段检测指标

### 路径2：路线→物理路段→检测数据
```sql
highway.code = 'G101' 
→ highway_segment.highway_id 
→ evaluation.highway_segment_id
```
**适用场景**：分析特定国高网路线质量

## 4. 典型筛选条件模板
### 时间范围筛选
```sql
WHERE check_year BETWEEN '2023-01-01' AND '2023-12-31'
```

### 管养责任单位筛选
```sql
WHERE management_unit_id IN (
  SELECT id FROM blade_dept_0227_to_li 
  WHERE ancestors LIKE '100,101%'
) /* 集团ID=100,路公司ID=101的下属单位 */
```

### 数据质量对比
```sql
WHERE data_source = 1 /* 仅分析集团检数据 */
GROUP BY data_source /* 对比不同检测来源的指标差异 */
```

## 5. 高频聚合模式
### 路段质量达标率统计
```sql
SELECT 
  AVG(CASE WHEN pqi_gp IN ('优','良') THEN 1 ELSE 0 END) AS pqi达标率,
  management_unit_name AS 管养单位
FROM evaluation_0227_to_li
GROUP BY management_unit_id
```

### 路线级指标趋势分析
```sql
SELECT 
  h.code AS 路线编码,
  YEAR(e.check_year) AS 年份,
  AVG(e.pqi) AS 平均PQI
FROM highway_0227_to_li h
JOIN highway_segment_0227_to_li hs ON h.id = hs.highway_id
JOIN evaluation_0227_to_li e ON hs.id = e.highway_segment_id
GROUP BY h.code, YEAR(e.check_year)
```

## 6. 性能优化提示
```sql
/* 使用以下索引加速查询 */
- evaluation_0227_to_li: 
  INDEX `data_source` (`check_year`,`data_source`) 
- blade_dept_0227_to_li: 
  INDEX `ancestors` (`ancestors`(50)) 
```

## 7. 数据血缘示例
```
集团报表 → 路公司 → 管理路段 → (物理路段 ↔ 国高网路线)
                ↑
            检测数据 → 管养单位
```

# 使用说明
当收到如"统计XX集团2023年各路段PQI优良率"的查询时：
1. 通过`blade_dept`找到集团ID对应的`ancestors`路径
2. 关联`highway_segment`获取管辖路段
3. 在`evaluation`表按`check_year`过滤后计算优良率
```