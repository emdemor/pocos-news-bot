from typing import List, Tuple

import chromadb
from chromadb.config import Settings
from chromadb.api.models.Collection import Collection
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction

from bot.vector_databases.base import VectorDB
from bot.data_models import News, BaseVectorDatabaseResult, VectorDatabaseNewsResult


class ChromaVectorDB(VectorDB):
    """
    A class representing a vector database using ChromaDB.
    """

    def __init__(self):
        """
        Initialize the ChromaVectorDB.
        """
        super().__init__()
        self.chroma_client = self._set_client()
        self.embedder = self._set_embedder()

    def get_most_similar(
        self, query: str, n_neighbors: int = 1000, n_results: int = 10, **kwargs
    ) -> List[BaseVectorDatabaseResult]:
        """
        Get the most similar results from the ChromaVectorDB based on the query.

        Args:
            query (str): The query string.
            n_neighbors (int): The number of neighbors to consider.
            n_results (int): The number of results to retrieve.
            **kwargs: Additional keyword arguments.

        Returns:
            List[BaseVectorDatabaseResult]: List of vector database results.
        """
        res = self.collection.query(
            query_texts=query,
            n_results=n_neighbors,
            **kwargs,
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
    def collection(self) -> Collection:
        """
        Get the ChromaDB collection.

        Returns:
            Collection: The ChromaDB collection.
        """
        return self.chroma_client.get_collection(
            self.bot_config.EMBEDDING_COLLECTION, embedding_function=self.embedder
        )

    def _set_embedder(self) -> SentenceTransformerEmbeddingFunction:
        """
        Set the embedder for ChromaVectorDB.

        Returns:
            SentenceTransformerEmbeddingFunction: The embedding function.
        """
        return SentenceTransformerEmbeddingFunction(
            model_name=self.bot_config.HUGGINGFACE_EMBEDDING_MODEL_NAME
        )

    def _set_client(self) -> chromadb.HttpClient:
        """
        Set the ChromaDB client.

        Returns:
            HttpClient: The ChromaDB client.
        """
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
    def _process_documents(key: str, value, k: int) -> Tuple[str, List[List]]:
        """
        Process documents by limiting lists to a specified length.

        Args:
            key (str): The key.
            value: The value to be processed.
            k (int): The limit for lists.

        Returns:
            Tuple[str, List[List]]: The processed key and value.
        """
        limit_list = lambda x: x[:k] if isinstance(x, list) else x
        processed_value = (
            [limit_list(x) for x in value] if isinstance(value, list) else None
        )
        return key, processed_value


class NewsChromaVectorDB(ChromaVectorDB):
    """
    A class representing a vector database specifically designed for news documents.
    Inherits from ChromaVectorDB.
    """

    @staticmethod
    def _format_search_result(*args) -> VectorDatabaseNewsResult:
        """
        Format the search result for news documents.

        Args:
            *args (Tuple): Tuple containing id, distance, document, and metadata.

        Returns:
            VectorDatabaseNewsResult: The formatted search result.
        """
        id, d, doc, meta = args
        if isinstance(meta.get("categories", ""), str):
            meta["categories"] = meta.get("categories", "").split("|")
        news = News(**dict([("id", id), ("document", doc)] + list(meta.items())))
        return VectorDatabaseNewsResult(distance=d, doc=news)
