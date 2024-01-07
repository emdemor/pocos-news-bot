from langchain.chat_models import ChatOpenAI
from langchain.memory.chat_memory import BaseChatMemory
from bot.handlers import PrivateHandler


class IntentionHandler(PrivateHandler):
    _prompt_key: str = "prompt_user_intention"
    _use_chat_history: bool = True

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
    def prompt_key(self):
        return self._prompt_key

    @property
    def use_chat_history(self):
        return self._use_chat_history

    @property
    def llm(self):
        return ChatOpenAI(model_name=self.llm_model, temperature=self.temperature)
