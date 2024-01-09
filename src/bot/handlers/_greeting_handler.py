from langchain.memory.chat_memory import BaseChatMemory
from langchain.chat_models import ChatOpenAI

from bot.handlers import PublicHandler
from bot.vector_databases.base import VectorDB


class GreetingHandler(PublicHandler):
    """
    A class representing a query handler for processing user queries.
    Inherits from PublicHandler.
    """

    _prompt_key: str = "prompt_greeting.json"
    _use_chat_history: bool = True
    _use_context: bool = True

    def __init__(
        self,
        llm_model: str,
        memory: BaseChatMemory,
        vector_database: VectorDB,
        temperature: float = 0,
        verbose: bool = True,
        llm_context_window_size: int = 4096,
        prompt_max_tokens: int = 3200,
    ):
        """
        Initialize the GreetingHandler.

        Args:
            llm_model (str): The language model for processing queries.
            memory (BaseChatMemory): The chat memory.
            vector_database (VectorDB): The vector database for query processing.
            temperature (float): The temperature for generating responses.
            verbose (bool): Whether to enable verbose mode.
            llm_context_window_size (int): The context window size for the language model.
            prompt_max_tokens (int): The maximum tokens for a prompt.
        """
        self._llm_model = llm_model
        self._memory = memory
        self._temperature = temperature
        self._verbose = verbose
        self._vector_database = vector_database
        self._llm_context_window_size = llm_context_window_size
        self._prompt_max_tokens = prompt_max_tokens

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
