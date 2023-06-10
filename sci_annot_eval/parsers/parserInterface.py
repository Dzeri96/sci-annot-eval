from abc import ABC, ABCMeta, abstractmethod
from typing import Any

from ..common.bounding_box import RelativeBoundingBox, AbsoluteBoundingBox

class Parser(metaclass=ABCMeta):
    
    @abstractmethod
    def parse_dict_relative(self, input: dict[str, Any]) -> list[RelativeBoundingBox]:
        pass

    @abstractmethod
    def parse_text_relative(self, input: str) -> list[RelativeBoundingBox]:
        pass

    @abstractmethod
    def parse_file_relative(self, path: str) -> list[RelativeBoundingBox]:
        pass

    @abstractmethod
    def parse_dict_absolute(self, input: dict[str, Any]) -> list[AbsoluteBoundingBox]:
        pass

    @abstractmethod
    def parse_text_absolute(self, input: str) -> list[AbsoluteBoundingBox]:
        pass

    @abstractmethod
    def parse_file_absolute(self, path: str) -> list[AbsoluteBoundingBox]:
        pass