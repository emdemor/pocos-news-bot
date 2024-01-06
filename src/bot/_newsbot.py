import os
import ast
import re
import json
from importlib import resources
from uuid import uuid4

import chromadb
from chromadb.config import Settings
from chromadb.utils import embedding_functions
import langchain_core
from langchain.chains import LLMChain
from langchain.chat_models import ChatOpenAI
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.memory import ConversationSummaryBufferMemory, ChatMessageHistory
from langchain.llms import OpenAI
from langchain.prompts import load_prompt
from loguru import logger
import tiktoken
from bot import BotConfig
from bot._local_memory import LocalMemory


_config = BotConfig()


def get_prompt(key):
    filepath = str(resources.files("bot.prompts").joinpath(f"{key}.json"))

    return load_prompt(filepath)


class NewsBot:
    def __init__(self, local_filepath: str):
        self.local_filepath = local_filepath

        self.llm = ChatOpenAI(model_name=_config.LLM_MODEL_NAME, temperature=0)
        self.llm_chat = ChatOpenAI(
            model_name=_config.LLM_MODEL_NAME,
            temperature=0,
            model_kwargs={"stop": ["HUMAN_INPUT", "IA:"]},
        )

        self.embeddings = HuggingFaceEmbeddings(
            model_name=_config.HUGGINGFACE_EMBEDDING_MODEL_NAME
        )
        self.embedder = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name=_config.HUGGINGFACE_EMBEDDING_MODEL_NAME
        )

        self.verbose_chains = False

        # Load utilitary prompts and chains
        self.prompt_intention = get_prompt("prompt_user_intention")
        self.prompt_standalone_question = get_prompt("prompt_standalone_question")

        # Load chat prompts and chains
        self.prompt_greeting = get_prompt("prompt_greeting")
        self.prompt_query = get_prompt("prompt_query")

        self.collection = self.get_chroma_collection()

        self.memory = ConversationSummaryBufferMemory(
            llm=OpenAI(temperature=0),
            chat_history=ChatMessageHistory(),
            return_messages=True,
            memory_key="chat_history",
            input_key="human_input",
            human_prefix="Human",
            ai_prefix="AI",
        )

        self.local_memory = LocalMemory(
            self.local_filepath, message_history=self.memory.chat_memory
        )

        self.memory.chat_memory = self.local_memory.message_history

    def get_chroma_collection(self):
        host_name = _config.VECTORDATABASE_HOSTNAME
        port = _config.VECTORDATABASE_PORT
        collection_name = _config.EMBEDDING_COLLECTION
        persist_directory = _config.VECTORDATABASE_PERSIST_DIRECTORY

        settings = Settings(
            allow_reset=True,
            anonymized_telemetry=True,
            persist_directory=persist_directory,
        )
        chroma_client = chromadb.HttpClient(
            host=host_name, port=port, settings=settings
        )

        return chroma_client.get_collection(
            collection_name, embedding_function=self.embedder
        )

    def predict(
        self, collection, query, n_neighbors: int = 1000, n_results: int = 10, **kwargs
    ):
        def f(key, value, k):
            def limit(x):
                if isinstance(x, list):
                    return x[:k]
                return x

            if isinstance(value, list):
                return (key, [limit(x) for x in value])
            return (key, None)

        res = collection.query(
            query_texts=query,
            n_results=n_neighbors,
            **kwargs
            # where={"metadata_field": "is_equal_to_this"},
            # where_document={"$contains":"search_string"}
        )

        return dict([f(key, value, n_results) for key, value in res.items()])

    def _set_local_context(self, content, meta):
        return (
            f"<data>{meta.get('date', '')}</data>\n"
            f"<titulo>{meta.get('title', '')}</titulo>\n"
            f"<autor>{meta.get('author', '')}</autor>\n"
            f"<link>{meta.get('link', '')}</link>\n"
            f"<conteudo>{content}</conteudo>\n"
        )

    def count_tokens(self, context: str) -> int:
        encoding = tiktoken.encoding_for_model(_config.LLM_MODEL_NAME)
        num_tokens = len(encoding.encode(context))

        return num_tokens

    def _set_query_content(self, documents, metadata):
        context_list = [
            self._set_local_context(content, meta)
            for content, meta in zip(documents, metadata)
        ]

        tokens = 4000
        max_tokens = 3600
        while tokens > max_tokens:
            tokens = self.count_tokens("\n".join(context_list))
            if tokens >= max_tokens:
                context_list.pop()

        return "\n".join(sorted(context_list))

    def get_content(self, query, n_results=10, n_neighbors=1000):
        result = self.predict(
            self.collection,
            query,
            n_results=n_results,
            n_neighbors=n_neighbors,
        )

        return self._set_query_content(result["documents"][0], result["metadatas"][0])

    def format_history_message(
        self, messages, human_prefix: str = "Human", ai_prefix: str = "AI"
    ):
        for message in messages:
            if isinstance(message, langchain_core.messages.human.HumanMessage):
                yield f"{human_prefix}: {message.content}\n"

            elif isinstance(message, langchain_core.messages.ai.AIMessage):
                yield f"{ai_prefix}: {message.content}\n"

    def get_standalone_question(self, message: str, *args, **kwargs) -> str:
        self.chain_standalone_question = LLMChain(
            llm=self.llm,
            prompt=self.prompt_standalone_question,
            verbose=self.verbose_chains,
        )

        result = self.chain_standalone_question.predict(
            history=self.memory, human_input=message
        )

        return result

    def get_user_intention(self, message: str, *args, **kwargs) -> str:
        self.chain_intention = LLMChain(
            llm=self.llm, prompt=self.prompt_intention, verbose=self.verbose_chains
        )

        return self.chain_intention.predict(
            history=self.memory, human_input=message
        )

    def handler_start_conversation(self, message: str, *args, **kwargs) -> str:

        logger.error(10 * "\n")
        logger.error("# handler_start_conversation -> ANTES")
        logger.error(str(self.memory))
        logger.error(10 * "\n")

        self.chain_greeting = LLMChain(
            llm=self.llm_chat,
            prompt=self.prompt_greeting,
            verbose=self.verbose_chains,
            memory=self.memory,
        )

        result = self.chain_greeting.predict(
            history=self.memory, human_input=message
        )

        logger.error(10 * "\n")
        logger.error("# handler_start_conversation -> DEPOIS")
        logger.error(str(self.memory))
        logger.error(10 * "\n")

        self.local_memory.update(message_history=self.memory.chat_memory)
        return result

    def handler_query(self, message: str, *args, **kwargs) -> str:

        logger.error(10 * "\n")
        logger.error("# handler_query -> ANTES")
        logger.error(str(self.memory))
        logger.error(10 * "\n")

        self.chain_query = LLMChain(
            llm=self.llm_chat,
            prompt=self.prompt_query,
            verbose=self.verbose_chains,
            memory=self.memory,
        )

        context = self.get_content(query=message)

        for i in range(3):
            response = self.chain_query.predict(
                history=self.memory, human_input=message, context=context
            )
            self.local_memory.update(message_history=self.memory.chat_memory)
            resp_dict = extract_dict_from_string(response)
            if len(resp_dict) > 0:
                _resposta = f'{resp_dict.get("resposta", "")}'
                _link = (
                    f'\n\nlink da noticia: {resp_dict.get("link", "")}'
                    if resp_dict.get("link", None)
                    else ""
                )
                return _resposta + _link
            continue

        logger.error(10 * "\n")
        logger.error("# handler_query -> DEPOIS")
        logger.error(str(self.memory))
        logger.error(10 * "\n")

        return response

    def handler_fallback(self, *args, **kwargs) -> str:
        return (
            "Desculpe, mas não posso responder a essa pergunta. "
            "Algo em que possa ajudar sobre notícias de Poços de Caldas e região?"
        )

    def execute(self, message: str):
        chat_history = "".join(
            self.format_history_message(self.memory.chat_memory.messages)
        )

        logger.error(10 * "\n")
        logger.error("CHAT HISTORY")
        logger.error(chat_history)
        logger.error(10 * "\n")

        standalone_question = self.get_standalone_question(
            message=message, history=chat_history
        )
        logger.debug(f"Pergunta original: {message}")
        logger.debug(f"Pergunta melhorada: {standalone_question}")

        intention = self.get_user_intention(
            message=standalone_question, history=chat_history
        )
        logger.debug(f"Intenção: {intention}")

        handlers = {
            "inicio de conversa": self.handler_start_conversation,
            "consulta de conteudo": self.handler_query,
            "": self.handler_fallback,
        }

        response = None
        for category, handler in handlers.items():
            if category in intention.lower().replace("ú", "u").replace("í", "i"):
                response = handler(
                    message=message, memory=self.memory, history=chat_history
                )
                break

        self.local_memory.update(message_history=self.memory.chat_memory)

        logger.error(10 * "\n")
        logger.error("CHAT HISTORY")
        logger.error(chat_history)
        logger.error(10 * "\n")

        return dict(response=response, execution_id=uuid4().hex)


def extract_dict_from_string(string):
    """
    Extrai um elemento JSON de uma string.

    Args:
    string: A string que contém o elemento JSON.

    Returns:
    O elemento JSON como um dicionário Python, ou None se não for possível extrair.
    """

    match = re.search(r"{([^}]+)}", string)
    if match is None:
        return dict()

    json_content = match.group(1)

    try:
        json_dict = json.loads("{" + json_content + "}")
        return json_dict
    except json.JSONDecodeError as err:
        logger.error(str(err))
        return dict()
