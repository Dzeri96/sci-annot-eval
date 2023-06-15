from enum import Enum
from abc import ABC, abstractmethod

# TODO: Change type in BoundingBox constructor to this enum
class TargetType(Enum):
    FIGURE = 'Figure'
    TABLE = 'Table'
    CAPTION = 'Caption'

class BoundingBox(ABC):
    @abstractmethod
    def __init__(self, type: str,  x: float, y: float, height: float, width: float, parent) -> None:
        self.type = type
        self.x = x
        self.y = y
        self.height = height
        self.width = width
        self.parent = parent

    def __str__(self) -> str:
        return f'{{id: {hash(self)}, type: {self.type}, x:{self.x}, y:{self.y}, width: {self.width}, height: {self.height}, parent: {hash(self.parent)}}}'

class AbsoluteBoundingBox(BoundingBox):
    def __init__(self, type: str, x: float, y: float, height: float, width: float, parent) -> None:
        super().__init__(type, x, y, height, width, parent)
        self.absolute= True

class RelativeBoundingBox(BoundingBox):
    def __init__(self, type: str, x: float, y: float, height: float, width: float, parent) -> None:
        super().__init__(type, x, y, height, width, parent)
        self.absolute= False

