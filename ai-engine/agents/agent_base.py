from abc import ABC, abstractmethod
from typing import Dict, Any

class BaseAgent(ABC):
    """Abstract base class for all LangChain agents."""

    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description

    @abstractmethod
    async def process(self, query: str, context: Dict[str, Any] = None) -> str:
        """Process the user query and return a response."""
        pass
