from langchain_openai import ChatOpenAI

from app.configs.settings import get_settings


def create_llm() -> ChatOpenAI:
    settings = get_settings()
    if not settings.llm_api_key.get_secret_value() or not settings.llm_model:
        raise ValueError("Configure LLM_API_KEY and LLM_MODEL before running agents")
    return ChatOpenAI(
        api_key=settings.llm_api_key.get_secret_value(),
        base_url=settings.llm_base_url or None,
        model=settings.llm_model,
        temperature=settings.llm_temperature,
        timeout=settings.llm_timeout_seconds,
        max_retries=settings.llm_max_retries,
    )
