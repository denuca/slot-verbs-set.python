from dataclasses import dataclass
from typing import List


@dataclass
class SlotCombination:
    symbols: List[str]
    words: List[str]
    difficulty: str
