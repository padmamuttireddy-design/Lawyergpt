class LawyerGPTException(Exception):
    pass


class ConversationNotFoundError(LawyerGPTException):
    pass


class MessageNotFoundError(LawyerGPTException):
    pass


class DocumentNotFoundError(LawyerGPTException):
    pass


class IngestionError(LawyerGPTException):
    pass


class VectorStoreError(LawyerGPTException):
    pass


class GenerationError(LawyerGPTException):
    pass


class FileTooLargeError(LawyerGPTException):
    pass


class InvalidFileTypeError(LawyerGPTException):
    pass
