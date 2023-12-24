from pydantic_settings import BaseSettings


class BotConfig(BaseSettings):
    LLM_MODEL_NAME: str = "gpt-3.5-turbo"
    HUGGINGFACE_EMBEDDING_MODEL_NAME: str = "clips/mfaq"
    VECTORDATABASE_HOSTNAME: str = "chroma-server"
    VECTORDATABASE_PORT: str = 8000
    VECTORDATABASE_PERSIST_DIRECTORY: str = "chroma_db"

    @property
    def EMBEDDING_COLLECTION(self) -> str:
        return self.HUGGINGFACE_EMBEDDING_MODEL_NAME.replace("/", "-")
