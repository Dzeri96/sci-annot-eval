from sci_annot_eval.common.sci_annot_annotation import Annotation
from ..common.bounding_box import AbsoluteBoundingBox
from . exporterInterface import Exporter
import json

class SciAnnotExporter(Exporter):
    # TODO: Stop breaking the rules of OOP!
    def export_to_dict(self, input: list[AbsoluteBoundingBox], canvas_width: int, canvas_height: int, **kwargs) -> dict:
        result = {
            'canvasHeight': canvas_height,
            'canvasWidth': canvas_width,
            'annotations': []
        }

        source = kwargs['source'] if 'source' in kwargs.keys() else 'Unknown'

        for annotation in input:
            if type(annotation) is not AbsoluteBoundingBox:
                raise TypeError(f'Annotation {annotation} is not of type AbsoluteBoundingBox!')
            generated_anno = {
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
                        "value": f"xywh=pixel:{annotation.x},{annotation.y},{annotation.width},{annotation.height}"
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

    def export_to_str(self, input: list[AbsoluteBoundingBox], canvas_width: int, canvas_height: int, **kwargs) -> str:
        res = self.export_to_dict(input, canvas_width, canvas_height, kwargs)
        return json.dumps(res)