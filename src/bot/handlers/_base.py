from abc import ABC, abstractmethod
from importlib import resources
from typing import List

from langchain.prompts import PromptTemplate
from langchain.chains.base import Chain
from langchain_core.language_models.chat_models import BaseChatModel
from langchain.prompts import load_prompt
from langchain_core.messages.human import HumanMessage
from langchain_core.messages.ai import AIMessage
from langchain.chains import LLMChain

from bot import BotConfig

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
    def prompt(self) -> PromptTemplate:
        return self.get_prompt(self.prompt_key)

    @property
    @abstractmethod
    def chain(self) -> Chain:
        pass

    @property
    @abstractmethod
    def use_chat_history(self) -> Chain:
        pass
    

    def get_chat_history(self) -> str:
        _class = self.__class__
        if hasattr(_class, "memory"):
            return "".join(
                self.format_history_message(self.memory.chat_memory.messages)
            )
        raise AttributeError(f"The class {_class.__name__} does not have the 'memory' attribute")

    def format_history_message(self, messages: List[HumanMessage | AIMessage]):
        for message in messages:
            if isinstance(message, HumanMessage):
                yield f"{config.HUMAN_PREFIX}: {message.content}\n"
    
            elif isinstance(message, AIMessage):
                yield f"{config.AI_PREFIX}: {message.content}\n"

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