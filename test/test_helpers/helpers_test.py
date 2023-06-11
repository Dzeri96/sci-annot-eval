from sci_annot_eval.helpers import helpers
from sci_annot_eval.common.bounding_box import AbsoluteBoundingBox, RelativeBoundingBox
import numpy as np
import pytest

class TestHelpers:

    def test_make_relative(self):
        x = 10
        y = 20
        height = 20
        width = 10

        page_height = 40
        page_width = 30

        input_box = AbsoluteBoundingBox(
            'figure',x,y,height,width,None
        )

        result_list = helpers.make_relative([input_box], page_width, page_height)
        relative_bounding_box = result_list[0]

        assert relative_bounding_box.x == (x / page_width)
        assert relative_bounding_box.y == (y / page_height)
        assert relative_bounding_box.width == (width / page_width)
        assert relative_bounding_box.height == (height / page_height)

    def test_make_absolute(self):
        x = 0.1
        y = 0.2
        height = 0.1
        width = 0.2

        page_height = 40
        page_width = 30

        input_box = RelativeBoundingBox(
            'figure',x,y,height,width,None
        )

        result_list = helpers.make_absolute([input_box], page_width, page_height)
        relative_bounding_box = result_list[0]

        assert relative_bounding_box.x == (x * page_width)
        assert relative_bounding_box.y == (y * page_height)
        assert relative_bounding_box.width == (width * page_width)
        assert relative_bounding_box.height == (height * page_height)


    @pytest.mark.parametrize(
        ['input_xywh', 'expected_xywh'], [
            ((10, 10, 80, 80), (25, 25, 50, 50)),
            ((35, 35, 59, 59), (35, 35, 40, 40)),
            # TODO: Change this behavior in next major version
            ((0, 0, 24, 24), (0, 0, 0, 0))
    ])
    def test_crop_to_content(self, input_xywh: tuple[int, int, int, int], expected_xywh: tuple[float, float, float, float]):
        test_img_array = np.full((100, 100),255, np.uint8)
        test_img_array[25:75, 25:75] = 0

        input_bb = AbsoluteBoundingBox(
            'test', input_xywh[0], input_xywh[1], input_xywh[3], input_xywh[2], None
        )

        xywh_result = helpers.crop_to_content(test_img_array, input_bb)

        assert xywh_result[0] == expected_xywh[0]
        assert xywh_result[1] == expected_xywh[1]
        assert xywh_result[2] == expected_xywh[2]
        assert xywh_result[3] == expected_xywh[3]

