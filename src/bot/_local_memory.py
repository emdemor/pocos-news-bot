import os
import json
from typing import Optional
from langchain.memory import ChatMessageHistory


JSON_ENCODING = "utf-8"


class LocalMemory:
    def __init__(
        self, localpath: str, message_history: Optional[ChatMessageHistory] = None
    ):
        self.localpath = localpath
        self.message_history = message_history

        if self.message_history is not None:
            self.dump()
        else:
            self.message_history = self._get_or_create_local_memory()

    def __dir__(self):
        return ["dump", "update", "clear"]

    def __repr__(self):
        return repr(self.message_history)

    def __str__(self):
        return str(self.message_history)

    def dump(self):
        atts = self.message_history.dict()
        with open(self.localpath, "w", encoding=JSON_ENCODING) as f:
            json.dump(atts, f)

    def update(self, message_history):
        self.message_history = message_history
        self.dump()

    def clear(self):
        self.message_history = ChatMessageHistory(messages=[])
        if self._check_if_local_file_exists():
            os.remove(self.localpath)

    def _check_if_local_file_exists(self):
        return os.path.exists(self.localpath)

    def _get_or_create_local_memory(self):
        if self._check_if_local_file_exists():
            return self._get_local_memory()
        return self._create_local_memory()

    def _get_local_memory(self):
        try:
            with open(self.localpath, "r", encoding=JSON_ENCODING) as f:
                local_memory_attrs = json.load(f)
            return ChatMessageHistory(**local_memory_attrs)
        except FileNotFoundError:
            raise LocalMemoryNotFoundError(f"File {self.localpath} not found.")

    def _create_local_memory(self):
        with open(self.localpath, "w", encoding=JSON_ENCODING) as f:
            json.dump({}, f)


class LocalMemoryNotFoundError(Exception):
    pass
