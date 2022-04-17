from abc import ABC, abstractmethod

class PredictionFieldMapper(ABC):

    @classmethod
    @property
    @abstractmethod
    def region_boundary(cls) -> str:
        pass

    @classmethod
    @property
    @abstractmethod
    def caption_boundary(cls) -> str:
        pass

    @classmethod
    @property
    @abstractmethod
    def figure_type(cls) -> str:
        pass


class Pdffigures2FieldMapper(PredictionFieldMapper):

    @classmethod
    @property
    def region_boundary(cls) -> str:
        return "regionBoundary"

    @classmethod
    @property
    def caption_boundary(cls) -> str:
        return "captionBoundary"

    @classmethod
    @property
    def figure_type(cls) -> str:
        return "figType"

class DeepfiguresFieldMapper (PredictionFieldMapper):

    @classmethod
    @property
    def region_boundary(cls) -> str:
        return "figure_boundary"

    @classmethod
    @property
    def caption_boundary(cls) -> str:
        return "caption_boundary"

    @classmethod
    @property
    def figure_type(cls) -> str:
        return "figure_type"