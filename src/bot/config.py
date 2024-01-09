from pydantic_settings import BaseSettings


class BotConfig(BaseSettings):
    LLM_MODEL_NAME: str = "gpt-3.5-turbo"
    LLM_CONTEXT_WINDOW_SIZE: int = 4096
    PROMPT_MAX_TOKENS: int = 3200
    HUGGINGFACE_EMBEDDING_MODEL_NAME: str = "clips/mfaq"
    VECTORDATABASE_HOSTNAME: str = "chroma-server"
    VECTORDATABASE_PORT: int = 8000
    VECTORDATABASE_PERSIST_DIRECTORY: str = "chroma_db"
    HUMAN_PREFIX: str = "Human"
    AI_PREFIX: str = "AI"

    @property
    def EMBEDDING_COLLECTION(self) -> str:
        return self.HUGGINGFACE_EMBEDDING_MODEL_NAME.replace("/", "-")
