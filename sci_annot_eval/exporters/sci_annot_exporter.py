from sci_annot_eval.common.sci_annot_annotation import Annotation, SciAnnotOutput
from ..common.bounding_box import AbsoluteBoundingBox, RelativeBoundingBox
from . exporterInterface import Exporter
import json
from typing import TypedDict, Any


class SciAnnotExporter(Exporter):
    def export_to_dict(self, input: list[RelativeBoundingBox], canvas_width: int, canvas_height: int, **kwargs) -> SciAnnotOutput:
        result: SciAnnotOutput = {
            'canvasHeight': canvas_height,
            'canvasWidth': canvas_width,
            'annotations': []
        }

        source = kwargs['source'] if 'source' in kwargs.keys() else 'Unknown'

        for annotation in input:
            if type(annotation) is not RelativeBoundingBox:
                raise TypeError(f'Annotation {annotation} is not of type RelativeBoundingBox!')
            absolute_x = annotation.x * canvas_width
            absolute_y = annotation.y * canvas_height
            absolute_height = annotation.height * canvas_height
            absolute_width = annotation.width * canvas_width
            generated_anno: Annotation = {
                "type": "Annotation",
                "body": [
                    {
                        "type": "TextualBody",
                        "purpose": "img-cap-enum",
                        "value": f"{annotation.type}"
                    }
                ],
                "target": {
                    "source": source,
                    "selector": {
                        "type": "FragmentSelector",
                        "conformsTo": "http://www.w3.org/TR/media-frags/",
                        "value": f"xywh=pixel:{absolute_x},{absolute_y},{absolute_width},{absolute_height}"
                    }
                },
                "@context": "http://www.w3.org/ns/anno.jsonld",
                "id": f"#{hash(annotation)}"
            }

            if(annotation.parent):
                generated_anno['body'].append({
                    "type": "TextualBody",
                    "purpose": "parent",
                    "value": f"#{hash(annotation.parent)}"
                })

            result['annotations'].append(generated_anno)

        return result

    def export_to_str(self, input: list[RelativeBoundingBox], canvas_width: int, canvas_height: int, **kwargs) -> str:
        res = self.export_to_dict(input, canvas_width, canvas_height, **kwargs)
        return json.dumps(res, indent=4)

    def export_to_file(
        self,
        input: list[RelativeBoundingBox],
        canvas_width: int,
        canvas_height: int,
        file_location: str,
        **kwargs
    ):
        res = self.export_to_str(input, canvas_width, canvas_height, **kwargs)
        with open(file_location, 'w') as f:
            f.write(res)
