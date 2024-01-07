from abc import ABC, abstractmethod

import chromadb
from chromadb.config import Settings
from chromadb.utils import embedding_functions

from bot.vector_databases import VectorDB, VectorDBCollection, get_collection


class ChromaCollection(VectorDBCollection):
    
    def get_most_similar(
        self, query: str, n_neighbors: int = 1000, n_results: int = 10, **kwargs
    ):
        res = self.collection.query(
            query_texts=query,
            n_results=n_neighbors,
            **kwargs
            # where={"metadata_field": "is_equal_to_this"},
            # where_document={"$contains":"search_string"}
        )

        return dict(
            [
                self._process_documents(key, value, n_results)
                for key, value in res.items()
            ]
        )

    @property
    def vector_database(self):
        return ChromaVectorDB()

    @property
    def collection(self):
        return self.vector_database.start()

    def _process_documents(key, value, k):
        limit_list = lambda x: x[:k] if isinstance(x, list) else x
        processed_value = (
            [limit_list(x) for x in value] if isinstance(value, list) else None
        )
        return key, processed_value


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
