from test.test_parsers.test_parserInterface import TstParserInterface
from sci_annot_eval.common.sci_annot_annotation import Annotation
from sci_annot_eval.common.bounding_box import TargetType
from sci_annot_eval.parsers.sci_annot_parser import SciAnnotParser
from sci_annot_eval.common.sci_annot_annotation import SciAnnotOutput
import pytest

@pytest.fixture
def reference_sci_annot_annotation() -> Annotation:
    result: Annotation = {
        '@context': "http://www.w3.org/ns/anno.jsonld",
        'type': "Annotation",
        'id': "test_id",
        'body': [
            {
             'type': "TextualBody",
             'purpose': "img-cap-enum",
             'value': 'Caption'
            },
            {
             'type': "TextualBody",
             'purpose': 'parent',
             'value': 'test_parent_id'
            }
        ],
        'target': {
            "source": "test_source",
            "selector": {
                "type": "FragmentSelector",
                "conformsTo": "http://www.w3.org/TR/media-frags/",
                "value": f"xywh=pixel:100,90,80,70"
            }
        }
    }

    return result

@pytest.fixture
def reference_sci_annot_input(reference_sci_annot_annotation: Annotation) -> SciAnnotOutput:
    parent_annotation: Annotation = {
        '@context': "http://www.w3.org/ns/anno.jsonld",
        'type': "Annotation",
        'id': "test_parent_id",
        'body': [
            {
             'type': "TextualBody",
             'purpose': "img-cap-enum",
             'value': 'Caption'
            },
        ],
        'target': {
            "source": "test_source",
            "selector": {
                "type": "FragmentSelector",
                "conformsTo": "http://www.w3.org/TR/media-frags/",
                "value": f"xywh=pixel:100,180,80,20"
            }
        }
    }

    return {"annotations": [reference_sci_annot_annotation, parent_annotation], "canvasHeight": 300, "canvasWidth": 200}

class TestSciAnnotParser(TstParserInterface):

    def test_get_annotation_type_should_return_proper_type(self, reference_sci_annot_annotation: Annotation):
        res = SciAnnotParser().get_annotation_type(reference_sci_annot_annotation)
        assert res == TargetType.CAPTION

    def test_get_annotation_type_should_throw_on_unknown_type(self, reference_sci_annot_annotation: Annotation):
        reference_sci_annot_annotation['body'][0]['value'] = "INVALID_TYPE"
        with pytest.raises(ValueError):
            SciAnnotParser().get_annotation_type(reference_sci_annot_annotation)

    def test_get_annotation_parent_id_should_return_correct_result(self, reference_sci_annot_annotation: Annotation):
        res = SciAnnotParser().get_annotation_parent_id(reference_sci_annot_annotation)
        assert res == 'test_parent_id'

    def test_get_annotation_parent_id_should_return_none_on_no_parent(self, reference_sci_annot_annotation: Annotation):
        reference_sci_annot_annotation['body'].pop(1)
        res = SciAnnotParser().get_annotation_parent_id(reference_sci_annot_annotation)
        assert res is None

    def test_parse_location_string_returns_correct_result(self, reference_sci_annot_annotation: Annotation):
        res = SciAnnotParser().parse_location_string(reference_sci_annot_annotation)
        assert res[0] == 100
        assert res[1] == 90
        assert res[2] == 80
        assert res[3] == 70

    def test_parse_dict_absolute_returns_correct_nr_of_annotations(
        self,
        reference_sci_annot_input: SciAnnotOutput
    ):
        res = SciAnnotParser().parse_dict_absolute(reference_sci_annot_input)
        assert len(res) == 2

    def test_parse_dict_absolute_correctly_maps_parent(
        self,
        reference_sci_annot_input: SciAnnotOutput
    ):
        res = SciAnnotParser().parse_dict_absolute(reference_sci_annot_input)
        assert res[0].parent is res[1]
        assert res[1].parent is None

    
    def test_parse_dict_relative_correctly_scales_dimensions(
        self,
        reference_sci_annot_input: SciAnnotOutput
    ):
        res = SciAnnotParser().parse_dict_relative(reference_sci_annot_input)
        ref_annot = res[0]
        assert ref_annot.x == 100/200
        assert ref_annot.y == 90/300
        assert ref_annot.width == 80/200
        assert ref_annot.height == 70/300