根据您提供的数据库表结构和需求，我将为您设计一个简化的数据库模型图和领域模型图，并给出一些关键的SQL查询示例。这将帮助您理解数据之间的关系以及如何通过这些关系来生成所需的分析报告。

### 1. 数据库模型图
以下是基于您提供的表结构的简化版数据库模型图：

- **blade_dept_0227_to_li**：机构表
- **evaluation_0227_to_li**：定检数据
- **highway_0227_to_li**：路线数据
- **highway_segment_0227_to_li**：路段数据
- **management_unit_0227_to_li**：管养单位
- **regular_contract_0227_to_li**：路面定检合同表
- **regular_unit_0227_to_li**：路面定检评定表

#### 关系：
- `evaluation_0227_to_li` 和 `highway_segment_0227_to_li` 通过 `highway_segment_id` 关联。
- `highway_segment_0227_to_li` 和 `highway_0227_to_li` 通过 `highway_id` 关联。
- `evaluation_0227_to_li` 和 `regular_unit_0227_to_li` 通过 `regular_unit_id` 关联。
- `regular_unit_0227_to_li` 和 `regular_contract_0227_to_li` 通过 `contract_id` 关联。
- `evaluation_0227_to_li` 和 `management_unit_0227_to_li` 通过 `management_unit_id` 关联。

### 2. 领域模型图
领域模型图描述了业务对象及其之间的关系。以下是基于您的需求的简化版领域模型图：

- **Route**（路线）
- **Segment**（路段）
- **EvaluationUnit**（评价单元）
- **ManagementUnit**（管养单位）
- **RegularContract**（定检合同）
- **RegularUnit**（定检单元）

#### 关系：
- **Route** 包含多个 **Segment**
- **Segment** 包含多个 **EvaluationUnit**
- **EvaluationUnit** 属于一个 **ManagementUnit**
- **RegularContract** 包含多个 **RegularUnit**
- **RegularUnit** 对应一个 **Segment**