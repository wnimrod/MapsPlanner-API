from typing import List, Optional, Literal

from openai import AsyncOpenAI
from pydantic import BaseModel

from MapsPlanner_API.settings import settings


class ChatGPTConfig(BaseModel):
    model: str = "gpt-3.5-turbo"
    role: Literal["user"] = "user"


class ChatGPTClient:
    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.chatgpt_api_key)
        self._default_config = ChatGPTConfig()

    async def query(
        self, queries: List[str], config: Optional[ChatGPTConfig] = None
    ) -> List[str]:
        config = config or self._default_config
        messages = [
            {"role": config.role, "content": query.strip()} for query in queries
        ]

        response = await self.client.chat.completions.create(
            model=config.model,
            messages=messages,
        )

        return [choice.message.content for choice in response.choices]


async_chatgpt_client = ChatGPTClient()
