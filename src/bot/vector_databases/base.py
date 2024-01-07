from abc import ABC, abstractmethod

from bot import BotConfig
from bot.vector_databases import ChromaVectorDB


def get_vector_database(label: str):
    _vdbs_mapping = {
        "chroma": ChromaVectorDB,
    }

    if label not in _vdbs_mapping:
        raise VectorDatabaseNotRecognizedError(
            f"VDB '{label}' not recognized."
        )

    return _vdbs_mapping[label]()


class VectorDB(ABC):
    def __init__(self):
        self.bot_config = BotConfig()

    @abstractmethod
    def start(self):
        pass

    @abstractmethod
    def _set_embedder(self):
        pass


class VectorDBCollection(ABC):
    @abstractmethod
    def get_most_similar(self):
        pass

    @property
    @abstractmethod
    def vector_database(self):
        pass

    @property
    @abstractmethod
    def collection(self):
        pass


class VectorDatabaseNotRecognizedError(Exception):
    pass
