from test.test_parsers.test_parserInterface import TstParserInterface
from sci_annot_eval.common.prediction_field_mapper import PredictionFieldMapper, Pdffigures2FieldMapper, DeepfiguresFieldMapper
from sci_annot_eval.parsers.pdffigures2_parser import PdfFigures2Parser
from typing import Type
from sci_annot_eval.common.bounding_box import TargetType
import pytest

# TODO: Add regionless-caption test

@pytest.fixture
def ref_pdffigures2_annotation():
    return {
    "width": 200,
    "height": 300,
    "figures": [
        {
            "caption": "Figure 1: MMPI profile of a patient (example); suppressors +0.5K, +0.4K, +1K, +0.2K a correction value from raw results of scale K added to raw results of selected clinical scales",
            "captionBoundary": {
                "x1": 100,
                "x2": 150,
                "y1": 90,
                "y2": 130
            },
            "figType": "Figure",
            "imageText": [],
            "name": "1",
            "page": 3,
            "regionBoundary": {
                "x1": 100,
                "x2": 120,
                "y1": 180,
                "y2": 210
            }
        }
    ],
    "regionless-captions": []
}

@pytest.fixture
def ref_deepfigures_annotation():
    return {
    "width": 200,
    "height": 300,
    "figures": [
        {
            "caption": "Figure 1: MMPI profile of a patient (example); suppressors +0.5K, +0.4K, +1K, +0.2K a correction value from raw results of scale K added to raw results of selected clinical scales",
            "caption_boundary": {
                "x1": 100,
                "x2": 150,
                "y1": 90,
                "y2": 130
            },
            "figure_type": "Figure",
            "imageText": [],
            "name": "1",
            "page": 3,
            "figure_boundary": {
                "x1": 100,
                "x2": 120,
                "y1": 180,
                "y2": 210
            }
        }
    ],
    "regionless-captions": []
}

class TestPdfFigures2Parser(TstParserInterface):
    
    @pytest.mark.parametrize(
        ["annotation_input_name", "pred_field_mapper"],
        [
            ("ref_pdffigures2_annotation", Pdffigures2FieldMapper),
            ("ref_deepfigures_annotation", DeepfiguresFieldMapper)
        ]
    )
    def test_get_annotation_type_should_return_proper_type(
            self,
            annotation_input_name,
            pred_field_mapper: Type[PredictionFieldMapper],
            request
    ):
        parser = PdfFigures2Parser(pred_field_mapper)
        input = request.getfixturevalue(annotation_input_name)
        res = parser.parse_dict_absolute(input)

        assert res[0].type == TargetType.FIGURE.value

    @pytest.mark.parametrize(
        ["annotation_input_name", "pred_field_mapper"],
        [
            ("ref_pdffigures2_annotation", Pdffigures2FieldMapper),
            ("ref_deepfigures_annotation", DeepfiguresFieldMapper)
        ]
    )
    def test_figure_boundary_is_parsed_correctly(
        self,
        annotation_input_name,
        pred_field_mapper: Type[PredictionFieldMapper],
        request
    ):
        parser = PdfFigures2Parser(pred_field_mapper)
        input = request.getfixturevalue(annotation_input_name)
        res = parser.parse_dict_absolute(input)

        figure = res[0]
        assert figure.x == 100
        assert figure.y == 180
        assert figure.width == 20
        assert figure.height == 30

    @pytest.mark.parametrize(
        ["annotation_input_name", "pred_field_mapper"],
        [
            ("ref_pdffigures2_annotation", Pdffigures2FieldMapper),
            ("ref_deepfigures_annotation", DeepfiguresFieldMapper)
        ]
    )
    def test_caption_boundary_is_parsed_correctly(
        self,
        annotation_input_name,
        pred_field_mapper: Type[PredictionFieldMapper],
        request
    ):
        parser = PdfFigures2Parser(pred_field_mapper)
        input = request.getfixturevalue(annotation_input_name)
        res = parser.parse_dict_absolute(input)

        caption = res[1]
        assert caption.x == 100
        assert caption.y == 90
        assert caption.width == 50
        assert caption.height == 40


    @pytest.mark.parametrize(
        ["annotation_input_name", "pred_field_mapper"],
        [
            ("ref_pdffigures2_annotation", Pdffigures2FieldMapper),
            ("ref_deepfigures_annotation", DeepfiguresFieldMapper)
        ]
    )
    def test_parse_dict_absolute_correctly_maps_parent(
        self,
        annotation_input_name,
        pred_field_mapper: Type[PredictionFieldMapper],
        request
    ):
        parser = PdfFigures2Parser(pred_field_mapper)
        input = request.getfixturevalue(annotation_input_name)
        res = parser.parse_dict_absolute(input)

        figure = res[0]
        caption = res[1]

        assert caption.parent is figure
