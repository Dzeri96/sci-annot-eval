from sci_annot_eval.common.bounding_box import RelativeBoundingBox
from . parserInterface import Parser
from .. common.bounding_box import AbsoluteBoundingBox, BoundingBox, RelativeBoundingBox
from ..common.sci_annot_annotation import Annotation
from .. helpers import helpers
import re
import json
from typing import Any, Optional

class SciAnnotParser(Parser):
    location_regex= re.compile(r'\d+(?:\.\d+)?')
    child_types = ['Caption']

    def get_annotation_type(self, annot: Annotation)-> str:
        for block in annot['body']:
            if block['purpose'] == 'img-cap-enum':
                return block['value']
        raise Exception(f'Annotation has no type: {annot}')

    def get_annotation_parent_id(self, annot: Annotation)-> Optional[str] :
        for block in annot['body']:
            if block['purpose'] == 'parent':
                return block['value']
        return None

    def parse_location_string(self, loc: str)-> tuple[float, float, float, float]:
        parsed_loc = self.location_regex.findall(loc)
        if (len(parsed_loc) != 4):
            raise Exception(f'Location string couldn\'t be parsed: {loc}')

        # Python's typing is not so clever yet...
        return (float(parsed_loc[0]), float(parsed_loc[1]), float(parsed_loc[2]), float(parsed_loc[3]))
        
    def parse_dict_absolute(self, input: dict) -> list[AbsoluteBoundingBox]:
    
        result: dict[AbsoluteBoundingBox, AbsoluteBoundingBox] = {}
        for annotation in input['annotations']:
            id = annotation['id']
            ann_type = self.get_annotation_type(annotation)
            x, y, width, height = self.parse_location_string(annotation['target']['selector']['value'])
            parent_id = None
            if ann_type in self.child_types:
                parent_id = self.get_annotation_parent_id(annotation)

            result[id] = AbsoluteBoundingBox(
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

        return res_list

    def parse_dict_relative(self, input: dict[str, Any]) -> list[RelativeBoundingBox]:
        canvas_height = int(input['canvasHeight'])
        canvas_width = int(input['canvasWidth'])

        return helpers.make_relative(self.parse_dict_absolute(input), canvas_width, canvas_height)

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