import chromadb
from chromadb.config import Settings
from chromadb.utils import embedding_functions

from bot.vector_databases.base import VectorDB
from bot.data_models import News, VectorDatabaseNewsResult


class ChromaVectorDB(VectorDB):
    def __init__(self):
        super().__init__()
        self.chroma_client = self._set_client()
        self.embedder = self._set_embedder()

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

        result = dict(
            [
                self._process_documents(key, value, n_results)
                for key, value in res.items()
            ]
        )

        return [
            self._format_search_result(*args)
            for args in zip(
                result["ids"][0],
                result["distances"][0],
                result["documents"][0],
                result["metadatas"][0],
            )
        ]

    @property
    def collection(self) -> chromadb.api.models.Collection.Collection:
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

    @staticmethod
    def _format_search_result(*args):
        id, d, doc, meta = args
        if isinstance(meta.get("categories", ""), str):
            meta["categories"] = meta.get("categories", "").split("|")
        news = News(**dict([("id", id), ("document", doc)] + list(meta.items())))
        return VectorDatabaseNewsResult(distance=d, news=news)

    @staticmethod
    def _process_documents(key, value, k):
        limit_list = lambda x: x[:k] if isinstance(x, list) else x
        processed_value = (
            [limit_list(x) for x in value] if isinstance(value, list) else None
        )
        return key, processed_value
