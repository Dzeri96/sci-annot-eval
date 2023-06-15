from abc import ABC
import pytest
from sci_annot_eval.common.bounding_box import TargetType
from sci_annot_eval.common.bounding_box import RelativeBoundingBox
from sci_annot_eval.exporters.exporterInterface import Exporter

@pytest.fixture
def reference_relative_bb_list() -> list[RelativeBoundingBox]:

    figure1 = RelativeBoundingBox(TargetType.FIGURE.value, 0.1, 0.1, 0.1, 0.1, None)
    figure1_caption = RelativeBoundingBox(TargetType.CAPTION.value, 0.1, 0.12, 0.02, 0.1, figure1)

    table1 = RelativeBoundingBox(TargetType.TABLE.value, 0.2, 0.2, 0.1, 0.1, None)
    
    no_parent_caption = RelativeBoundingBox(TargetType.CAPTION.value, 0.2, 0.4, 0.02, 0.1, None)

    return [figure1, figure1_caption, table1, no_parent_caption]
    

class TstExporterInterface(ABC):
    """Interface to be implemented by every exporter test.
    Name changed to avoid instantiation by pytest.
    """

def test_equal_number_of_exporters_and_test_classes():
    assert len(Exporter.__subclasses__()) == len(TstExporterInterface.__subclasses__())