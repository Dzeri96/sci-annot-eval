from abc import ABC, ABCMeta, abstractmethod

from ..common.bounding_box import BoundingBox

class Parser(ABC):
    
    @abstractmethod
    def parse_dict(self, input: dict, make_relative: bool) -> list[BoundingBox]:
        pass

    @abstractmethod
    def parse_text(self, input: str, make_relative: bool) -> list[BoundingBox]:
        pass

    @abstractmethod
    def parse_file(self, path: str, make_relative: bool) -> list[BoundingBox]:
        pass