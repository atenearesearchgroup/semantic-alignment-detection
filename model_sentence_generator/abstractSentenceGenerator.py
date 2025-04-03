from abc import ABC, abstractmethod
from typing import List


class AbstractSentenceGenerator(ABC):
    @abstractmethod
    def get_sentences(self) -> List[str]:
        pass

    @abstractmethod
    def generate_sentences(self):
        pass
