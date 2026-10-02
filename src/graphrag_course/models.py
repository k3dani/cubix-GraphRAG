"""LLM és embedding kliensek OpenAI-kompatibilis API-n (a base_url dönti el, mi van mögötte)."""

from langchain_openai import ChatOpenAI, OpenAIEmbeddings

from graphrag_course import config


def get_llm() -> ChatOpenAI:
    extra_body = (
        {"chat_template_kwargs": {"enable_thinking": False}}
        if config.LLM_DISABLE_THINKING
        else None
    )
    return ChatOpenAI(
        model=config.LLM_MODEL,
        base_url=config.LLM_BASE_URL,
        api_key=config.LLM_API_KEY,
        temperature=0,
        extra_body=extra_body,
    )


def get_embeddings() -> OpenAIEmbeddings:
    return OpenAIEmbeddings(
        model=config.EMBEDDING_MODEL,
        base_url=config.EMBEDDING_BASE_URL,
        api_key=config.EMBEDDING_API_KEY,
        # nem-OpenAI modellnél nyers szöveget kell küldeni, nem tiktoken-tokeneket
        check_embedding_ctx_length=False,
    )
