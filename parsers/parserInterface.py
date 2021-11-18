from abc import ABC, ABCMeta, abstractmethod

from . bounding_box import BoundingBox

class Parser(ABC):
    
    @abstractmethod
    def parse_dict(self, input: dict) -> list[BoundingBox]:
        pass

    @abstractmethod
    def parse_text(self, input: str) -> list[BoundingBox]:
        pass