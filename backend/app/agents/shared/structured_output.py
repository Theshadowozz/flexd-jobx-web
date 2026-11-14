import json
from typing import Literal

from langchain_core.messages import HumanMessage, SystemMessage
from pydantic import BaseModel


class LangChainStructuredModel:
    """Lazy OpenAI-compatible adapter. Choose method supported by the actual endpoint."""

    def __init__(
        self,
        model=None,
        *,
        method: Literal["json_schema", "function_calling", "json_mode"] = "json_schema",
    ):
        self._model = model
        self.method = method

    async def generate(self, schema: type[BaseModel], prompt: str, payload: dict) -> BaseModel:
        if self._model is None:
            from app.configs.llm import create_llm

            self._model = create_llm()
        runnable = self._model.with_structured_output(schema, method=self.method)
        messages = [
            SystemMessage(
                content=prompt + "\nOutput JSON schema: " + json.dumps(schema.model_json_schema())
            ),
            HumanMessage(content=json.dumps(payload, ensure_ascii=False, default=str)),
        ]
        result = await runnable.ainvoke(messages)
        return schema.model_validate(result)
