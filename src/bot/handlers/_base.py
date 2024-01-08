from abc import ABC, abstractmethod
from importlib import resources
from typing import List

import tiktoken
from langchain.prompts import PromptTemplate
from langchain.chains.base import Chain
from langchain_core.language_models.chat_models import BaseChatModel
from langchain.prompts import load_prompt
from langchain_core.messages.human import HumanMessage
from langchain_core.messages.ai import AIMessage
from langchain.chains import LLMChain

from bot import BotConfig
from bot.data_models import News, VectorDatabaseNewsResult

config = BotConfig()


class Handler(ABC):
    prompts_folder: str = "bot.prompts"
    human_prefix: str = config.HUMAN_PREFIX
    ai_prefix: str = config.AI_PREFIX

    def __init__(self):
        pass

    def get_prompt(self, key: str) -> PromptTemplate:
        filepath = str(resources.files(self.prompts_folder).joinpath(f"{key}.json"))
        return load_prompt(filepath)

    def predict(self, message) -> str:
        params = {}
        if self.use_chat_history:
            params.update(dict(history=self.get_chat_history()))

        if self.use_context:
            params.update(dict(context=self.get_context(message)))

        return self.chain.predict(human_input=message, **params)

    @property
    @abstractmethod
    def llm(self) -> BaseChatModel:
        pass

    @property
    @abstractmethod
    def prompt_key(self) -> str:
        pass

    @property
    @abstractmethod
    def temperature(self) -> float:
        pass

    @property
    @abstractmethod
    def verbose(self) -> bool:
        pass

    @property
    @abstractmethod
    def llm_model(self) -> str:
        pass

    @property
    @abstractmethod
    def memory(self):
        pass

    @property
    @abstractmethod
    def vector_database(self):
        pass

    @property
    def prompt(self) -> PromptTemplate:
        return self.get_prompt(self.prompt_key)

    @property
    @abstractmethod
    def chain(self) -> Chain:
        pass

    @property
    @abstractmethod
    def use_chat_history(self) -> bool:
        pass

    @property
    @abstractmethod
    def use_context(self) -> bool:
        pass

    @property
    @abstractmethod
    def llm_context_window_size(self) -> int:
        pass

    @property
    @abstractmethod
    def prompt_max_tokens(self) -> int:
        pass

    def get_chat_history(self) -> str:
        _class = self.__class__

        if not hasattr(_class, "memory"):
            raise AttributeError(
                f"The class {_class.__name__} does not have the 'memory' attribute"
            )

        if not self.use_chat_history:
            raise ValueError(
                f"You cannot get the chat history if 'use_chat_history=False'"
            )

        return "".join(self._format_history_message(self.memory.chat_memory.messages))

    def get_context(self, query, n_results=10, n_neighbors=1000):
        _class = self.__class__

        if not hasattr(_class, "vector_database"):
            raise AttributeError(
                f"The class {_class.__name__} does not have the 'vector_database' attribute"
            )

        if not self.use_context:
            raise ValueError(f"You cannot get context if 'use_context=False'")

        results = self.vector_database.get_most_similar(
            query, n_neighbors=n_neighbors, n_results=n_results
        )
        return self._set_query_content(results)

    def _format_history_message(self, messages: List[HumanMessage | AIMessage]):
        for message in messages:
            if isinstance(message, HumanMessage):
                yield f"{config.HUMAN_PREFIX}: {message.content}\n"

            elif isinstance(message, AIMessage):
                yield f"{config.AI_PREFIX}: {message.content}\n"

    def _count_tokens(self, context: str) -> int:
        encoding = tiktoken.encoding_for_model(self.llm_model)
        num_tokens = len(encoding.encode(context))
        return num_tokens

    @staticmethod
    def _format_news(news: News, order: int) -> str:
        return (
            f"\n<noticia_{order}>\n"
            f"\t<data>{news.date}</data>\n"
            f"\t<titulo>{news.title}</titulo>\n"
            f"\t<autor>{news.author}</autor>\n"
            f"\t<link>{news.link}</link>\n"
            f"\t<conteudo>{news.document}</conteudo>\n"
            f"</noticia_{order}>"
        )

    def _set_query_content(self, results: List[VectorDatabaseNewsResult]) -> str:
        context_list = [self._format_news(res.news, i+1) for i, res in enumerate(results)]
        tokens = self.llm_context_window_size
        max_tokens = self.prompt_max_tokens
        while tokens > max_tokens:
            tokens = self._count_tokens("\n".join(context_list))
            if tokens >= max_tokens:
                context_list.pop()
        return "\n".join(sorted(context_list))


class PrivateHandler(Handler, ABC):
    @property
    def chain(self) -> Chain:
        return LLMChain(
            llm=self.llm,
            prompt=self.prompt,
            verbose=self.verbose,
        )


class PublicHandler(Handler, ABC):
    @property
    def chain(self) -> Chain:
        return LLMChain(
            llm=self.llm,
            prompt=self.prompt,
            verbose=self.verbose,
            memory=self.memory,
        )
