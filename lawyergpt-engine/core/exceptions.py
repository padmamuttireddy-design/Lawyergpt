class EngineException(Exception):
    pass


class LoaderError(EngineException):
    pass


class ChunkerError(EngineException):
    pass


class EmbeddingError(EngineException):
    pass


class VectorStoreError(EngineException):
    pass


class RetrieverError(EngineException):
    pass


class GenerationError(EngineException):
    pass
