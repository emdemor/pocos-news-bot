from abc import ABC, abstractmethod

from bot import BotConfig


class VectorDB(ABC):
    def __init__(self):
        self.bot_config = BotConfig()

    @property
    @abstractmethod
    def collection(self):
        pass

    @abstractmethod
    def get_most_similar(self):
        pass

    @abstractmethod
    def _set_embedder(self):
        pass
