import os
import ast
from importlib import resources

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


_config = BotConfig()


def get_prompt(key):
    filepath = str(
        resources.files("bot.prompts").joinpath(f"{key}.json")
    )

    return load_prompt(filepath)

class NewsBot():

    def __init__(self):

        self.llm = ChatOpenAI(model_name=_config.LLM_MODEL_NAME, temperature=0)
        self.llm_chat = ChatOpenAI(model_name=_config.LLM_MODEL_NAME, temperature=0, model_kwargs={"stop": ["HUMAN_INPUT", "IA:"]})

        self.embeddings = HuggingFaceEmbeddings(model_name=_config.HUGGINGFACE_EMBEDDING_MODEL_NAME)
        self.embedder = embedding_functions.SentenceTransformerEmbeddingFunction(model_name=_config.HUGGINGFACE_EMBEDDING_MODEL_NAME)

        self.verbose_chains = True
        
        # Load utilitary prompts and chains
        self.prompt_intention = get_prompt("prompt_user_intention")
        self.prompt_standalone_question = get_prompt("prompt_standalone_question")
        
        # Load chat prompts and chains
        self.prompt_greeting = get_prompt("prompt_greeting")
        self.prompt_query = get_prompt("prompt_query")

        self.collection = self.get_chroma_collection()

    def get_chroma_collection(self):

        host_name = _config.VECTORDATABASE_HOSTNAME
        port = _config.VECTORDATABASE_PORT
        collection_name = _config.EMBEDDING_COLLECTION
        persist_directory = _config.VECTORDATABASE_PERSIST_DIRECTORY
        
        settings = Settings(allow_reset=True, anonymized_telemetry=True, persist_directory=persist_directory)
        chroma_client = chromadb.HttpClient(host=host_name, port = port, settings=settings)
        
        return chroma_client.get_collection(collection_name, embedding_function=self.embedder)
    
    def predict(self, collection, query, n_neighbors: int = 1000, n_results: int = 10, **kwargs):

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
      
        return  dict([f(key, value, n_results)  for key, value in res.items()])
    
    def _set_local_context(self, content, meta):
        return (
            f"<data>{meta['date']}</data>\n"
            f"<titulo>{meta['title']}</titulo>\n"
            f"<autor>{meta['author']}</autor>\n"
            f"<link>{meta['link']}</link>\n"
            f"<conteudo>{content}</conteudo>\n"
        )
    
    def count_tokens(self, context: str) -> int:
        encoding = tiktoken.encoding_for_model(_config.LLM_MODEL_NAME)
        num_tokens = len(encoding.encode(context))
        
        return num_tokens
    
    def _set_query_content(self, documents, metadata):
        context_list = [self._set_local_context(content, meta) for content, meta in zip(documents, metadata)]

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
    
        return self._set_query_content(result['documents'][0], result['metadatas'][0])

    def format_history_message(self, messages, human_prefix: str = 'Human', ai_prefix: str = 'AI'):
        for message in messages:
            if isinstance(message, langchain_core.messages.human.HumanMessage):
                yield f"{human_prefix}: {message.content}\n"
            
            elif isinstance(message, langchain_core.messages.ai.AIMessage):
                yield f"{ai_prefix}: {message.content}\n"

    def get_standalone_question(self, message: str, *args, **kwargs) -> str:

        self.chain_standalone_question = LLMChain(
            llm=self.llm, prompt=self.prompt_standalone_question, verbose=self.verbose_chains
        )

        return self.chain_standalone_question.predict(history=kwargs["history"], human_input=message)
    
    def get_user_intention(self, message: str, *args, **kwargs) -> str:

        self.chain_intention = LLMChain(
            llm=self.llm, prompt=self.prompt_intention, verbose=self.verbose_chains
        )

        return self.chain_intention.predict(history=kwargs["history"], human_input=message)
    
    def handler_start_conversation(self, message: str, *args, **kwargs) -> str:

        self.chain_greeting = LLMChain(
            llm=self.llm_chat, prompt=self.prompt_greeting, verbose=self.verbose_chains, memory=kwargs["memory"]
        )

        return self.chain_greeting.predict(history=kwargs["history"], human_input=message)

    def handler_query(self, message: str, *args, **kwargs) -> str:

        self.chain_query = LLMChain(
            llm=self.llm_chat, prompt=self.prompt_query, verbose=self.verbose_chains, memory=kwargs["memory"]
        )

        context = self.get_content(query=message)

        response = self.chain_query.predict(history=kwargs["history"], human_input=message, context=context)
        resp_dict = ast.literal_eval(response)

        return f'{resp_dict["resposta"]}\n\nNotícia: {resp_dict["link"]}'

    def handler_fallback(self, *args, **kwargs) -> str:

        return (
            "Desculpe, mas não posso responder a essa pergunta. "
            "Algo em que possa ajudar sobre notícias de Poços de Caldas e região?"
        )

    def execute(self, message: str):

        memory = ConversationSummaryBufferMemory(
            llm=OpenAI(temperature=0),
            chat_history=ChatMessageHistory(),
            return_messages=True,
            memory_key="chat_history",
            input_key="human_input",
            human_prefix="Human",
            ai_prefix="AI"
        )
        chat_history = "".join(self.format_history_message(memory.chat_memory.messages))
        
        standalone_question = self.get_standalone_question(message=message, history=chat_history)
        logger.debug(f"Pergunta original: {message}")
        logger.debug(f"Pergunta melhorada: {standalone_question}")
        
        intention = self.get_user_intention(message=standalone_question, history=chat_history)
        logger.debug(f"Intenção: {intention}")
        
        handlers = {
            "inicio de conversa": self.handler_start_conversation,
            "consulta de conteudo": self.handler_query,
            "": self.handler_fallback
        }

        response = None
        for category, handler in handlers.items():
            if category in intention.lower().replace("ú", "u").replace("í", "i"):
                response = handler(
                    message=message,
                    memory=memory,
                    history=chat_history
                )
                break

        logger.info(f">>> Resposta: {response}")
        
        return response
