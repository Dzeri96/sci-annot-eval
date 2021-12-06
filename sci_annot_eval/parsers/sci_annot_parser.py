from . parserInterface import Parser
from .. common.bounding_box import BoundingBox, RelativeBoundingBox
from ..common.sci_annot_annotation import Annotation
from .. helpers.helpers import make_absolute
import re
import json

class SciAnnotParser(Parser):
    location_regex= re.compile(r'\d+(?:\.\d+)?')
    child_types = ['Caption']

    def get_annotation_type(self, annot: Annotation)-> str:
        for block in annot['body']:
            if block['purpose'] == 'img-cap-enum':
                return block['value']
        raise Exception(f'Annotation has no type: {annot}')

    def get_annotation_parent_id(self, annot: Annotation)-> str :
        for block in annot['body']:
            if block['purpose'] == 'parent':
                return block['value']
        return None

    def parse_location_string(self, loc: str)-> tuple[float, float, float, float]:
        parsed_loc = self.location_regex.findall(loc)
        if (len(parsed_loc) != 4):
            raise Exception(f'Location string couldn\'t be parsed: {loc}')
        return tuple(float(entry) for entry in parsed_loc)
        
    def parse_dict(self, input: dict, make_absolute: bool) -> list[BoundingBox]:
        canvas_height = input['canvasHeight']
        canvas_width = input['canvasWidth']

        result: dict[RelativeBoundingBox] = {}
        for annotation in input['annotations']:
            id = annotation['id']
            ann_type = self.get_annotation_type(annotation)
            x, y, width, height = self.parse_location_string(annotation['target']['selector']['value'])
            parent_id = None
            if ann_type in self.child_types:
                parent_id = self.get_annotation_parent_id(annotation)

            result[id] = RelativeBoundingBox(
                ann_type,
                x,
                y,
                height,
                width,
                parent_id,
            )

        for id, annotation in result.items():
            if annotation.parent:
                annotation.parent = result[annotation.parent]

        res_list = list(result.values())

        if make_absolute:
            res_list = make_absolute(res_list, canvas_width, canvas_height)

        return res_list

    def parse_text(self, input: str, make_absolute: bool) -> list[BoundingBox]:
        return self.parse_dict(json.loads(input), make_absolute)