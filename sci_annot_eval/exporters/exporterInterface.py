from abc import ABC, abstractmethod

from .. common.bounding_box import BoundingBox

class Exporter(ABC):
    
    @abstractmethod
    def export_to_dict(self, input: list[BoundingBox], canvas_width: int, canvas_height: int, **kwargs) -> dict:
        pass

    @abstractmethod
    def export_to_str(self, input: list[BoundingBox], canvas_width: int, canvas_height: int, **kwargs) -> str:
        pass