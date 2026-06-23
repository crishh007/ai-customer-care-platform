# ASSIGNED TO: AI-2
# Base Agent class - all agents must inherit from this
# Implement:
#   - Abstract method: handle(query, context) → response string
#   - Common logging and error handling
#   - Shared memory interface

from abc import ABC, abstractmethod

class BaseAgent(ABC):
    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    async def handle(self, query: str, context: dict) -> str:
        # Each agent implements its own logic here
        pass

    def log(self, message: str):
        print(f"[{self.name}] {message}")
