import cv2 as cv
import numpy as np
from ..common.bounding_box import AbsoluteBoundingBox, RelativeBoundingBox

def delete_multiple_elements(list_object, indices):
    indices = sorted(indices, reverse=True)
    for idx in indices:
        list_object.pop(idx)

def make_absolute(bbox_list: list[RelativeBoundingBox], canvas_width: int, canvas_height: int) -> list[AbsoluteBoundingBox]:
    result_dict = {}
    for box in bbox_list:
        if type(box) is not RelativeBoundingBox:
            raise TypeError(f'Annotation {box} is not of type RelativeBoundingBox!')
        abs_box = AbsoluteBoundingBox(
            box.type,
            box.x*canvas_width,
            box.y*canvas_height,
            box.height*canvas_height,
            box.width*canvas_width,
            box.parent
        )
        result_dict[box] = abs_box
    
    # Replace old parent references with new ones
    for id, annotation in result_dict.items():
            if annotation.parent:
                annotation.parent = result_dict[annotation.parent]

    return list(result_dict.values())

def make_relative(bbox_list: list[AbsoluteBoundingBox], canvas_width: int, canvas_height: int) -> list[RelativeBoundingBox]:
    result_dict = {}
    for box in bbox_list:
        if type(box) is not AbsoluteBoundingBox:
            raise TypeError(f'Annotation {box} is not of type AbsoluteBoundingBox!')
        abs_box = RelativeBoundingBox(
            box.type,
            box.x/float(canvas_width),
            box.y/float(canvas_height),
            box.height/float(canvas_height),
            box.width/float(canvas_width),
            box.parent
        )
        result_dict[box] = abs_box
    
    # Replace old parent references with new ones
    for id, annotation in result_dict.items():
            if annotation.parent:
                annotation.parent = result_dict[annotation.parent]

    return list(result_dict.values())

        
def crop_to_content(
    img: np.ndarray,
    orig_coords: RelativeBoundingBox,
    threshold: int= 248
) -> tuple[float, float, float, float]:
    ox = int(orig_coords.x)
    oy = int(orig_coords.y)
    ow = int(orig_coords.width)
    oh = int(orig_coords.height)
    selected_slice = img[oy:oy+oh+1, ox:ox+ow+1]
    is_color = len(img.shape) == 3 and img.shape[2] == 3
    if is_color:
        gray = cv.cvtColor(selected_slice, cv.COLOR_BGR2GRAY)
    else:
        gray = selected_slice
    gray = 255 * (gray < threshold).astype(np.uint8)
    coords = cv.findNonZero(gray)  # Find all non-zero points (text)
    x, y, w, h = cv.boundingRect(coords)  # Find minimum spanning bounding box
    #return (orig_coords.x+x, orig_coords.y + y, w, h)
    return (ox+x, oy+y, w, h)

def crop_all_to_content(
    img_path: str,
    orig_annots: list[RelativeBoundingBox],
    threshold: int= 248
) -> list[RelativeBoundingBox]:
    img = cv.imread(img_path)
    print(f'img_shape: {img.shape}')
    result_dict = {}
    for annot in orig_annots:
        x, y, w, h = crop_to_content(img, annot, threshold)
        cropped = RelativeBoundingBox(
            annot.type,
            x,
            y,
            h,
            w,
            annot.parent
        )

        result_dict[annot] = cropped

    # Replace old parent references with new ones
    for id, annotation in result_dict.items():
        if annotation.parent:
            annotation.parent = result_dict[annotation.parent]

    return list(result_dict.values())