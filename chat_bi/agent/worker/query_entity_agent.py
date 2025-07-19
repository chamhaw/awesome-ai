from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm
from pydantic import Field
from pydantic import BaseModel
from one_agent.app.config import ModelConfig


SYSTEM_PROMPT = """
you are a entity extractor, needing to extract entity from questions.
"""

USER_PROMPT = """

Given a user's question, please extract the entity in the question and output the result in json format. 


<instructions>
- The extracted entities consist of two parts: one is a normal entity, and the other is a time entity.
- The normal entity is the keyword of this query.
- The time entity, after releasing the time entity in advance, it is necessary to convert the time entity into a format defined according to time_rules and quarter_explanation.
</instructions>

Here is some quarter explanation:

<quarter_explanation>
- 财年季度/Quarter	区别于自然年的季度，财年季度划分规则如下：Q1包括6,7,8月，Q2包括9,10,11月，Q3包括12,1,2月，Q4包括3,4,5月。Q1代表的是第一财年季度
- 自然年季度/Season	自然年季度划分如下，SP指Spring season，包括1,2,3月；SU指Summer season，包括4,5,6月；FA指Fall season，包括7,8,9月；HO指Holiday season，包括10,11,12月。
- If the fiscal year is not mentioned in the question, it is assumed to be the natural year.
</quarter_explanation>


Here is time rules:

<time_rules>

<day_rules>
{{%4d}}年{{%2d}}月{{%2d}}日
今年{{%2d}}月{{%2d}}日
去年{{%2d}}月{{%2d}}日
前年{{%2d}}月{{%2d}}日
明年{{%2d}}月{{%2d}}日
后年{{%2d}}月{{%2d}}日
本月{{%2d}}日
上月{{%2d}}日
上上月{{%2d}}日
下月{{%2d}}日
上月今天
上上月今天
今天
昨天
前天
明天
后天
本周第{{%d}}天
本月最后一天
上月最后一天
今年{{%2d}}月最后一天

</day_rules>
<month_rules>
{{%4d}}年{{%2d}}月
今年{{%2d}}月
去年{{%2d}}月
前年{{%2d}}月
明年{{%2d}}月
后年{{%2d}}月
本月
上月
上上月
下月
去年本月
</month_rules>

<year_rules>
{{%4d}}年
今年
去年
前年
明年
后年
</year_rules>

<fiscal_year_rules>
FY{{%2d}}
{{%4d}}财年
当前财年
上一财年
</fiscal_year_rules>



<half_year_rules>
{{%4d}}年上半年
{{%4d}}年下半年
今年上半年
今年下半年
去年上半年
去年下半年
上半年
下半年
</half_year_rules>


<season_rules>
{{%4d}}年第{{%d}}季度
今年第{{%d}}季度
去年第{{%d}}季度
前年第{{%d}}季度
明年第{{%d}}季度
后年第{{%d}}季度
本季度
上季度
下季度
去年本季度
</season_rules>

<quarter_rules>
{{%4d}}年第{{%d}}财年季度
今年第{{%d}}财年季度
去年第{{%d}}财年季度
前年第{{%d}}财年季度
明年第{{%d}}财年季度
后年第{{%d}}财年季度
本财年季度
上财年季度
下财年季度
去年本财年季度
</quarter_rules>

<week_rules>
本周星期{{%1d}}
上周星期{{%1d}}
上上周星期{{%1d}}
下周星期{{%1d}}
下下周星期{{%1d}}
本周
上周
上上周
下周
下下周
{{%4d}}年第{{%2d}}周
今年第{{%2d}}周
去年第{{%2d}}周
前年第{{%2d}}周
本月第{{%1d}}周
上月第{{%1d}}周
{{%4d}}年{{%2d}}月最后一周
本月最后一周
上月最后一周
上上月最后一周
{{%4d}}年{{%2d}}月第{{%1d}}周
今年{{%2d}}月第{{%1d}}周
去年{{%2d}}月第{{%1d}}周
前年{{%2d}}月第{{%1d}}周
{{%4d}}年{{%2d}}月第{{%1d}}个完整周
今年{{%2d}}月第{{%1d}}个完整周
去年{{%2d}}月第{{%1d}}个完整周
前年{{%2d}}月第{{%1d}}个完整周
{{%4d}}年第{{%1d}}个完整周
今年第{{%2d}}个完整周
去年第{{%2d}}个完整周
前年第{{%2d}}个完整周
本月第{{%1d}}个完整周
上月第{{%1d}}个完整周
本月最后一个完整周
上月最后一个完整周
上上月最后一个完整周


</week_rules>


<time_period_rules>
近{{\\d+}}年
近{{\\d+}}个月
近{{\\d+}}周
近{{\\d+}}个完整年
近{{\\d+}}个完整季度
近{{\\d+}}个完整月
近{{\\d+}}个完整周
不包含今天的近{{\\d+}}天
包含当前季度的近{{\\d+}}个季度

</time_period_rules>


<special_rules>
D11
{{\\d+}}天内
</special_rules>

</time_rules>

Just output the json, no other explanatory text is needed. If there is a conflict, special_rules have a higher priority.
<example>
question : 本年度的销量是多少
answer : 
{{
    "normal_entity": ["本年度","销量"]
    "time_entity": {{
        "本年度" : "今年"
    }}
}}

question : 这个season上架的产品的销量是多少
answer : 
{{
    "normal_entity": ["season","上架","产品","销量"]
    "time_entity": {{
        "season" : "本季度"
    }}
}}

</example>

【question】
{question}
【answer】
"""


class QueryEntityOutput(BaseModel):
    normal_entity: list[str] = Field("普通实体")
    time_entity: dict[str, str] = Field("时间实体")

inst = f"{SYSTEM_PROMPT} \n\n {USER_PROMPT}"


query_entity_agent = LlmAgent(
    name="query_entity_agent",
    model=LiteLlm(
        model=ModelConfig.GENERAL_MODEL,
        response_format={"type": "json_object"}  # 强制LLM以JSON格式返回
    ),
    instruction=inst,
    description="抽取问题实体",
    output_schema=QueryEntityOutput,
    output_key="query_entity_output",
    disallow_transfer_to_parent=True,
    disallow_transfer_to_peers=True
)
