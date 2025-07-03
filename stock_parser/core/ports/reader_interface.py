from abc import ABC, abstractmethod

class ReaderInterface(ABC):
    @abstractmethod
    def read(self, path: str) -> list: pass
