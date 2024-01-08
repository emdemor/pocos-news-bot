from typing import Optional
from langchain.chat_models import ChatOpenAI
from langchain.memory.chat_memory import BaseChatMemory
from bot.handlers import PrivateHandler
from bot.vector_databases.base import VectorDB


class StandaloneHandler(PrivateHandler):
    _prompt_key: str = "prompt_standalone_question"
    _use_chat_history: bool = True
    _use_context: bool = False
    _llm_context_window_size: Optional[int] = None
    _prompt_max_tokens: Optional[int] = None
    _vector_database: Optional[VectorDB] = None

    def __init__(
        self,
        llm_model: str,
        memory: BaseChatMemory,
        temperature: float = 0,
        verbose: bool = True,
    ):
        self._llm_model = llm_model
        self._memory = memory
        self._temperature = temperature
        self._verbose = verbose

    @property
    def temperature(self):
        return self._temperature

    @property
    def verbose(self):
        return self._verbose

    @property
    def llm_model(self):
        return self._llm_model

    @property
    def memory(self):
        return self._memory

    @property
    def vector_database(self):
        return self._vector_database

    @property
    def prompt_key(self):
        return self._prompt_key

    @property
    def use_chat_history(self):
        return self._use_chat_history

    @property
    def use_context(self):
        return self._use_context

    @property
    def llm_context_window_size(self):
        return self._llm_context_window_size

    @property
    def prompt_max_tokens(self):
        return self._prompt_max_tokens

    @property
    def llm(self):
        return ChatOpenAI(model_name=self.llm_model, temperature=self.temperature)
