class FallbackHandler:
    """
    A class representing a standalone handler for processing standalone questions.
    Inherits from PrivateHandler.
    """

    def predict(self) -> str:
        """
        Generate a fallback message based on the input message.

        Args:
            message (str): The input message.

        Returns:
            str: The generated message.
        """

        return (
            "Desculpe, mas não posso responder a essa pergunta. "
            "Algo em que possa ajudar sobre notícias de Poços de Caldas e região?"
        )
