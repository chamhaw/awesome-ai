from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm

from one_agent.app.config import ModelConfig

PROMPT =  """
You are a data analysis expert in the retail industry

As a professional data analyst, you are now asked a question by a user, and you need to analyze the data provided.

<instructions>
- Analyze the data based on the provided data, without creating non-existent data. It is crucial to only analyze the provided data.
- Perform relevant correlation analysis on the relationships between the data.
- The data related to the user's question is in a JSON result, which has been broken down into multiple sub-questions, including the sub-questions, queries, SQL, and data_result.
- response in chinese
</instructions>


The user question is：{question}

The data related to the question is：{sub_tasks_execute_data}

"""

data_analysis_agent = LlmAgent(
    name="data_analyse_agent",
    model=LiteLlm(model=ModelConfig.GENERAL_MODEL),
    instruction=PROMPT,
    description="结合多步任务的执行结果分析问题，得出结论",
)