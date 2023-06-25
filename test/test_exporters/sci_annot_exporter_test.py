from test.test_exporters.test_exporterInterface import TstExporterInterface, reference_relative_bb_list
from sci_annot_eval.common.bounding_box import RelativeBoundingBox
from sci_annot_eval.exporters.sci_annot_exporter import SciAnnotExporter
from sci_annot_eval.parsers.sci_annot_parser import SciAnnotParser, Annotation
from sci_annot_eval.common.sci_annot_annotation import SciAnnotOutput
import pytest

@pytest.fixture
def sci_annot_exporter_result(reference_relative_bb_list: list[RelativeBoundingBox]) -> SciAnnotOutput:
    exporter = SciAnnotExporter()
    return exporter.export_to_dict(reference_relative_bb_list, 500, 1000, source='test')

class TestSciAnnotExporter(TstExporterInterface):

    def find_annotation_by_hash(self, sci_annot_output: SciAnnotOutput, hash: int) -> Annotation:
        for annotation in sci_annot_output['annotations']:
            if annotation['id'] == f'#{hash}':
                return annotation #type: ignore
        
        raise Exception("Annotation not found!")

    def test_export_to_dict_has_all_annotations(
            self,
            reference_relative_bb_list: list[RelativeBoundingBox],
            sci_annot_exporter_result: SciAnnotOutput
    ):
        
        for bounding_box in reference_relative_bb_list:
            self.find_annotation_by_hash(sci_annot_exporter_result, hash(bounding_box))

    def test_export_to_dict_exports_correct_canvas_size(
            self,
            sci_annot_exporter_result: SciAnnotOutput
    ):
        assert sci_annot_exporter_result['canvasHeight'] == 1000
        assert sci_annot_exporter_result['canvasWidth'] == 500

    def test_export_to_dict_scales_bounding_boxes(
            self,
            reference_relative_bb_list: list[RelativeBoundingBox],
            sci_annot_exporter_result: SciAnnotOutput
    ):
        for bounding_box in reference_relative_bb_list:
            scaled_annotation = self.find_annotation_by_hash(sci_annot_exporter_result, hash(bounding_box))
            # TODO: Make parsing independent
            x, y, w, h = SciAnnotParser().parse_location_string(scaled_annotation)
            assert x == bounding_box.x * 500
            assert y == bounding_box.y * 1000
            assert w == bounding_box.width * 500
            assert h == bounding_box.height * 1000

    def test_export_to_dict_exports_correct_bb_classes(
            self,
            reference_relative_bb_list: list[RelativeBoundingBox],
            sci_annot_exporter_result: SciAnnotOutput
    ):
        for bounding_box in reference_relative_bb_list:
            found_annotation = self.find_annotation_by_hash(sci_annot_exporter_result, hash(bounding_box))
            assert found_annotation["body"][0]["value"] == bounding_box.type