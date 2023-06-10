from . parserInterface import Parser
from sci_annot_eval.common.bounding_box import AbsoluteBoundingBox, BoundingBox, RelativeBoundingBox, TargetType
from sci_annot_eval.common.prediction_field_mapper import PredictionFieldMapper
from .. helpers import helpers
import json
from typing import Any, Type

class PdfFigures2Parser(Parser):
    """This parser works for both Pdffigures2 and Deepfigures
    """
    def __init__(self, field_mapper: Type[PredictionFieldMapper]):
        self.field_mapper = field_mapper

    def extract_x12y12(self, boundaries: dict[str, float]) -> tuple[float, float, float, float]:
        x = boundaries['x1']
        y = boundaries['y1']
        x2 = boundaries['x2']
        y2 = boundaries['y2']
        w = x2 - x
        h = y2 - y

        return x, y, w, h


    def parse_dict_absolute(self, input: dict[str, Any]) -> list[AbsoluteBoundingBox]:
        result: list[AbsoluteBoundingBox] = []

        figures = input['figures']
        for figure in figures:
            fig_x, fig_y, fig_w, fig_h = self.extract_x12y12(figure[self.field_mapper.region_boundary])
            fig_type = figure[self.field_mapper.figure_type]
            fig_bbox = AbsoluteBoundingBox(fig_type, fig_x, fig_y, fig_h, fig_w, None)
            result.append(fig_bbox)

            if(self.field_mapper.caption_boundary in figure.keys()):
                cap_x, cap_y, cap_w, cap_h = self.extract_x12y12(figure[self.field_mapper.caption_boundary])
                result.append(AbsoluteBoundingBox(
                    TargetType.CAPTION.value, cap_x, cap_y, cap_h, cap_w, fig_bbox
                ))

        regionless_captions = []
        if 'regionless-captions' in input.keys():
            regionless_captions = input['regionless-captions']

        for r_caption in regionless_captions:
            r_cap_x, r_cap_y, r_cap_w, r_cap_h = self.extract_x12y12(r_caption['boundary'])
            result.append(AbsoluteBoundingBox(
                TargetType.CAPTION.value, r_cap_x, r_cap_y, r_cap_h, r_cap_w, None
            ))
                    
        return result
    
    def parse_dict_relative(self, input: dict[str, Any]) -> list[RelativeBoundingBox]:
        return helpers.make_relative(self.parse_dict_absolute(input), int(input['width']), int(input['height']))

    def parse_text_absolute(self, input: str) -> list[AbsoluteBoundingBox]:
        return self.parse_dict_absolute(json.loads(input))
    
    def parse_text_relative(self, input: str) -> list[RelativeBoundingBox]:
        return self.parse_dict_relative(json.loads(input))

    def parse_file_absolute(self, path: str) -> list[AbsoluteBoundingBox]:
        with open(path, 'r') as fd:
            return self.parse_dict_absolute(json.load(fd))
        
    def parse_file_relative(self, path: str) -> list[RelativeBoundingBox]:
        with open(path, 'r') as fd:
            return self.parse_dict_relative(json.load(fd))