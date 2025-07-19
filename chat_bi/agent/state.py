from typing import Dict, Any, Optional, AsyncGenerator

from google.adk.agents import BaseAgent
from google.adk.agents.invocation_context import InvocationContext
from google.adk.events import Event, EventActions


class StateUpdateAgent(BaseAgent):
    """
    提供状态更新功能的基础Agent类
    """

    def update_state(self, state_data: Dict[str, Any], ctx: Optional[InvocationContext] = None) -> Event:
        """
        通用方法用于更新状态，支持合并列表和字典类型
        
        Args:
            state_data: 需要更新的状态数据，键值对形式
            ctx: 调用上下文，用于获取当前状态
            
        Returns:
            更新状态的Event对象
        """
        return Event(author=self.name, actions=EventActions(state_delta=state_data))
