"""Contract every AI advisor backend must implement.

Advisors only ever receive data already stored in the engagement file.
They never touch the network target, and their output is never executed
automatically - it is surfaced to the operator for review.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class AdviceResult:
    provider: str
    text: str


class AdvisorProvider(ABC):
    name: str = "base"

    @abstractmethod
    def advise(self, prompt: str) -> AdviceResult:
        """Send `prompt` (already-rendered context, no live network data) and
        return the model's free-text suggestion."""
        raise NotImplementedError
