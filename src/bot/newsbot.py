from uuid import uuid4

from langchain.memory import ConversationSummaryBufferMemory, ChatMessageHistory
from langchain.llms import OpenAI
from loguru import logger

from bot import BotConfig
from bot.vector_databases import get_vector_database
from bot.handlers import (
    StandaloneHandler,
    QueryHandler,
    IntentionHandler,
    GreetingHandler,
    FallbackHandler,
)


config = BotConfig()


class NewsBot:

    """
    A class representing a News Bot for handling user queries and interactions.
    """

    def __init__(self, verbose: bool = True):
        """
        Initialize the NewsBot.

        Args:
            verbose (bool): Whether to enable verbose mode.
        """
        self.verbose = verbose

        self.vdb = get_vector_database("chroma")

        self.memory = ConversationSummaryBufferMemory(
            llm=OpenAI(temperature=0),
            chat_history=ChatMessageHistory(),
            return_messages=True,
            memory_key="chat_history",
            input_key="human_input",
            human_prefix=config.HUMAN_PREFIX,
            ai_prefix=config.AI_PREFIX,
        )

        self.standalone_handler = StandaloneHandler(
            llm_model=config.LLM_MODEL_NAME, memory=self.memory, verbose=verbose
        )
        self.intention_handler = IntentionHandler(
            llm_model=config.LLM_MODEL_NAME, memory=self.memory, verbose=verbose
        )
        self.query_handler = QueryHandler(
            llm_model=config.LLM_MODEL_NAME,
            memory=self.memory,
            vector_database=self.vdb,
            verbose=verbose,
        )
        self.greeting_handler = GreetingHandler(
            llm_model=config.LLM_MODEL_NAME,
            memory=self.memory,
            vector_database=self.vdb,
            verbose=verbose,
        )
        self.fallback_handler = FallbackHandler()

    def execute(self, message: str):
        """
        Execute the NewsBot to handle user input.

        Args:
            message (str): The user input message.

        Returns:
            dict: A dictionary containing the response and execution ID.
        """
        improved_message = self.standalone_handler.predict(message)
        logger.debug(f"Pergunta original: {message}")
        logger.debug(f"Pergunta melhorada: {improved_message}")

        intention = self.intention_handler.predict(improved_message)
        logger.debug(f"Intenção: {intention}")

        handlers = {
            "inicio de conversa": self.greeting_handler,
            "consulta de conteudo": self.query_handler,
            "": self.fallback_handler,
        }

        response = None
        for category, handler in handlers.items():
            if category in intention.lower().replace("ú", "u").replace("í", "i"):
                response = handler.predict(improved_message)
                break

        return dict(response=response, execution_id=uuid4().hex)
