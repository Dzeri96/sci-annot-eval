from typing import TypedDict
from . parserInterface import Parser
from . bounding_box import BoundingBox
import re
import json

class Annotation(TypedDict):
    type: str
    body: list[dict]
    target: dict
    id: str

class SciAnnotParser(Parser):
    location_regex= re.compile(r'\d+\.\d+')
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
        

    def parse_dict(self, input: dict) -> list[BoundingBox]:
        canvas_height = input['canvasHeight']
        canvas_width = input['canvasWidth']

        result: dict[BoundingBox] = {}
        for annotation in input['annotations']:
            id = annotation['id']
            type = self.get_annotation_type(annotation)
            x, y, width, height = self.parse_location_string(annotation['target']['selector']['value'])
            parent_id = None
            if type in self.child_types:
                parent_id = self.get_annotation_parent_id(annotation)

            result[id] = BoundingBox(
                type,
                x/canvas_width,
                y/canvas_height,
                height/canvas_height,
                width/canvas_width,
                parent_id
            )

        for id, annotation in result.items():
            if annotation.parent:
                annotation.parent = result[annotation.parent]

        return list(result.values())

    def parse_text(self, input: str) -> list[BoundingBox]:
        return self.parse_dict(json.loads(input))
                
x = SciAnnotParser()
