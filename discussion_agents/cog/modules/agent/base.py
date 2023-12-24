"""Base agent interface class."""

from abc import ABC
from pydantic import BaseModel
from typing import Any

class BaseAgent(BaseModel, ABC):
    """Base agent class providing a general interface for agent operations."""

    def plan(self) -> Any:
        """Optionally implementable method to plan an action or set of actions."""
        raise NotImplementedError("Plan method not implemented.")

    def reflect(self) -> Any:
        """Optionally implementable method to reflect on the current state or past actions."""
        raise NotImplementedError("Reflect method not implemented.")

    def score(self) -> Any:
        """Optionally implementable method to score or evaluate something."""
        raise NotImplementedError("Score method not implemented.")
