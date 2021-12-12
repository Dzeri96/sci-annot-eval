from . parserInterface import Parser
from sci_annot_eval.common.bounding_box import BoundingBox, RelativeBoundingBox, TargetType
from .. helpers import helpers
import json
from typing import cast

class PdfFigures2Parser(Parser):
    def extract_x12y12(self, boundaries: dict) -> tuple[float, float, float, float]:
        x = boundaries['x1']
        y = boundaries['y1']
        x2 = boundaries['x2']
        y2 = boundaries['y2']
        w = x2 - x
        h = y2 - y

        return x, y, w, h


    def parse_dict(self, input: dict, make_absolute: bool) -> list[BoundingBox]:
        result: list[RelativeBoundingBox] = []

        figures = input['figures']
        for figure in figures:
            fig_x, fig_y, fig_w, fig_h = self.extract_x12y12(figure['regionBoundary'])
            fig_type = figure['figType']
            fig_bbox = RelativeBoundingBox(fig_type, fig_x, fig_y, fig_h, fig_w, None)
            result.append(fig_bbox)

            if('captionBoundary' in figure.keys()):
                cap_x, cap_y, cap_w, cap_h = self.extract_x12y12(figure['captionBoundary'])
                result.append(RelativeBoundingBox(
                    TargetType.CAPTION.value, cap_x, cap_y, cap_h, cap_w, fig_bbox
                ))

        regionless_captions = input['regionless-captions']

        for r_caption in regionless_captions:
            r_cap_x, r_cap_y, r_cap_w, r_cap_h = self.extract_x12y12(r_caption['boundary'])
            result.append(RelativeBoundingBox(
                TargetType.CAPTION.value, r_cap_x, r_cap_y, r_cap_h, r_cap_w, None
            ))

        if make_absolute:
            return cast(list[BoundingBox],helpers.make_absolute(result, int(input['width']), int(input['height'])))
        
        return cast(list[BoundingBox], result)

    def parse_text(self, input: str, make_absolute: bool) -> list[BoundingBox]:
        return self.parse_dict(json.loads(input), make_absolute)

    def parse_file(self, path: str, make_absolute: bool) -> list[BoundingBox]:
        with open(path, 'r') as fd:
            return self.parse_dict(json.load(fd), make_absolute)