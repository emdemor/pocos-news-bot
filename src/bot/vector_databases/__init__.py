from bot.vector_databases._chroma import NewsChromaVectorDB
from bot.vector_databases.exceptions import VectorDatabaseNotRecognizedError

__all__ = [
    "ChromaVectorDB",
    "get_vector_database",
]


def get_vector_database(label: str):
    _vdbs_mapping = {
        "chroma": NewsChromaVectorDB,
    }

    if label not in _vdbs_mapping:
        raise VectorDatabaseNotRecognizedError(f"VDB '{label}' not recognized.")

    return _vdbs_mapping[label]()
