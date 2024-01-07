from abc import ABC, abstractmethod
from altair import Literal

import chromadb
from chromadb.config import Settings
from chromadb.utils import embedding_functions

from bot import BotConfig


COLLECTION_TYPES = chromadb.api.models.Collection.Collection
VECTOR_DATABASES_TYPES = Literal["chroma"]


def get_collection(vector_database: VECTOR_DATABASES_TYPES):
    _vdbs_mapping = {
        "chroma": ChromaVectorDB,
    }

    if vector_database not in _vdbs_mapping:
        raise VectorDatabaseNotRecognizedError(f"VDB '{vector_database}' not recognized.")

    return _vdbs_mapping[vector_database]().start()


class VectorDB(ABC):
    def __init__(self):
        self.bot_config = BotConfig()

    @abstractmethod
    def start(self) -> COLLECTION_TYPES:
        pass

    @abstractmethod
    def _set_embedder(self):
        pass


class ChromaVectorDB(VectorDB):
    def __init__(self):
        super().__init__()
        self.chroma_client = self._set_client()
        self.embedder = self._set_embedder()

    def start(self) -> chromadb.api.models.Collection.Collection:
        return self.chroma_client.get_collection(
            self.bot_config.EMBEDDING_COLLECTION, embedding_function=self.embedder
        )

    def _set_embedder(self):
        return embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name=self.bot_config.HUGGINGFACE_EMBEDDING_MODEL_NAME
        )

    def _set_client(self):
        _settings = Settings(
            allow_reset=True,
            anonymized_telemetry=True,
            persist_directory=self.bot_config.VECTORDATABASE_PERSIST_DIRECTORY,
        )
        return chromadb.HttpClient(
            host=self.bot_config.VECTORDATABASE_HOSTNAME,
            port=self.bot_config.VECTORDATABASE_PORT,
            settings=_settings,
        )


class VectorDatabaseNotRecognizedError(Exception):
    pass
