from abc import ABC, abstractmethod
from typing import Mapping
from .. common.bounding_box import RelativeBoundingBox

class Exporter(ABC):
    
    @abstractmethod
    def export_to_dict(self, input: list[RelativeBoundingBox], canvas_width: int, canvas_height: int, **kwargs) -> Mapping:
        pass

    @abstractmethod
    def export_to_str(self, input: list[RelativeBoundingBox], canvas_width: int, canvas_height: int, **kwargs) -> str:
        pass
    
    @abstractmethod
    def export_to_file(self, input: list[RelativeBoundingBox], canvas_width: int, canvas_height: int, file_location: str, **kwargs):
        pass