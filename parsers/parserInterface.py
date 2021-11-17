from abc import ABC, ABCMeta, abstractmethod
from enum import Enum

from . bounding_box import BoundingBox
class TargetClass(Enum):
    FIGURE = 'Figure',
    TABLE = 'Table',
    CAPTION = 'Caption'


class Parser(ABC):
    
    @abstractmethod
    def parse_dict(self, input: dict) -> list[BoundingBox]:
        pass

    @abstractmethod
    def parse_text(self, input: str) -> list[BoundingBox]:
        pass