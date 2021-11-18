from . parsers.bounding_box import BoundingBox, TargetType
from . parsers.sci_annot_parser import SciAnnotParser
from . helpers import helpers
import math
import numpy as np
import lapsolver

SCALE_FACTOR = 1000
IOU_THRESHOLD = 0.8

sci_annot_json_text_1 = '{"appVersion":"0.1.0","secondCounter":"39","annotations":[{"type":"Annotation","body":[{"type":"TextualBody","purpose":"img-cap-enum","value":"Figure"}],"target":{"source":"https://upload.wikimedia.org/wikipedia/commons/d/dc/Skyscrapers_of_Shinjuku_2009_January_(revised).jpg","selector":{"type":"FragmentSelector","conformsTo":"http://www.w3.org/TR/media-frags/","value":"xywh=pixel:2496.68310546875,780.6927490234375,281.119873046875,66.40625"}},"@context":"http://www.w3.org/ns/anno.jsonld","id":"#ee9eabcc-06e2-4ff2-bdc7-202ac7da935a"},{"type":"Annotation","body":[{"type":"TextualBody","purpose":"img-cap-enum","value":"Caption"},{"type":"TextualBody","purpose":"parent","value":"#ee9eabcc-06e2-4ff2-bdc7-202ac7da935a"}],"target":{"source":"https://upload.wikimedia.org/wikipedia/commons/d/dc/Skyscrapers_of_Shinjuku_2009_January_(revised).jpg","selector":{"type":"FragmentSelector","conformsTo":"http://www.w3.org/TR/media-frags/","value":"xywh=pixel:2308.963623046875,1087.2264404296875,329.66455078125,222.746337890625"}},"@context":"http://www.w3.org/ns/anno.jsonld","id":"#118d15d1-33aa-4e01-a59f-4f77fe633e9e"},{"type":"Annotation","body":[{"type":"TextualBody","purpose":"img-cap-enum","value":"Table"}],"target":{"source":"https://upload.wikimedia.org/wikipedia/commons/d/dc/Skyscrapers_of_Shinjuku_2009_January_(revised).jpg","selector":{"type":"FragmentSelector","conformsTo":"http://www.w3.org/TR/media-frags/","value":"xywh=pixel:2306.736083984375,690.7379150390625,151.467529296875,35.63946533203125"}},"@context":"http://www.w3.org/ns/anno.jsonld","id":"#73a7df7c-031c-442b-8e2f-75691ceb09e8"},{"type":"Annotation","body":[{"type":"TextualBody","purpose":"img-cap-enum","value":"Caption"},{"type":"TextualBody","purpose":"parent","value":"#73a7df7c-031c-442b-8e2f-75691ceb09e8"}],"target":{"source":"https://upload.wikimedia.org/wikipedia/commons/d/dc/Skyscrapers_of_Shinjuku_2009_January_(revised).jpg","selector":{"type":"FragmentSelector","conformsTo":"http://www.w3.org/TR/media-frags/","value":"xywh=pixel:2146.35888671875,982.53564453125,155.92236328125,69.0513916015625"}},"@context":"http://www.w3.org/ns/anno.jsonld","id":"#84192d0f-a4f8-47a6-b1ff-395794b34905"}],"feedback":"Evo proradio je", "canvasHeight": 1858, "canvasWidth": 3400}'

sci_annot_json_text_2 = '{"appVersion":"0.1.0","secondCounter":"39","annotations":[{"type":"Annotation","body":[{"type":"TextualBody","purpose":"img-cap-enum","value":"Figure"}],"target":{"source":"https://upload.wikimedia.org/wikipedia/commons/d/dc/Skyscrapers_of_Shinjuku_2009_January_(revised).jpg","selector":{"type":"FragmentSelector","conformsTo":"http://www.w3.org/TR/media-frags/","value":"xywh=pixel:2494.94873046875,780.9441528320312,290.699951171875,45.89996337890625"}},"@context":"http://www.w3.org/ns/anno.jsonld","id":"#95dc6c69-32ba-46dd-844d-20b01ee2d23a"},{"type":"Annotation","body":[{"type":"TextualBody","purpose":"img-cap-enum","value":"Table"}],"target":{"source":"https://upload.wikimedia.org/wikipedia/commons/d/dc/Skyscrapers_of_Shinjuku_2009_January_(revised).jpg","selector":{"type":"FragmentSelector","conformsTo":"http://www.w3.org/TR/media-frags/","value":"xywh=pixel:2309.267822265625,698.0511474609375,148.188720703125,25.01885986328125"}},"@context":"http://www.w3.org/ns/anno.jsonld","id":"#7c3b7892-35a1-4bae-84b4-f50e2a53f04a"},{"type":"Annotation","body":[{"type":"TextualBody","purpose":"img-cap-enum","value":"Caption"},{"type":"TextualBody","purpose":"parent","value":"#95dc6c69-32ba-46dd-844d-20b01ee2d23a"}],"target":{"source":"https://upload.wikimedia.org/wikipedia/commons/d/dc/Skyscrapers_of_Shinjuku_2009_January_(revised).jpg","selector":{"type":"FragmentSelector","conformsTo":"http://www.w3.org/TR/media-frags/","value":"xywh=pixel:2314.884033203125,1102.15966796875,315.671142578125,240.1424560546875"}},"@context":"http://www.w3.org/ns/anno.jsonld","id":"#c074e9a0-72c3-49fd-965d-40d7672500fd"}],"feedback":"Evo proradio je", "canvasHeight": 1858, "canvasWidth": 3400}'

def calc_L2_matrix(predictions: list[BoundingBox], ground_truth: list[BoundingBox]) -> np.ndarray:
    result = []
    for prediction in predictions:
        pred_centre_x = (prediction.x + (prediction.width / 2)) * SCALE_FACTOR
        pred_centre_y = (prediction.y + (prediction.height / 2)) * SCALE_FACTOR
        column = []
        for truth in ground_truth:
            truth_centre_x = (truth.x + (truth.width / 2)) * SCALE_FACTOR
            truth_centre_y = (truth.y + (truth.height / 2)) * SCALE_FACTOR
            L2_distance = math.sqrt((pred_centre_x - truth_centre_x) ** 2 + (pred_centre_y - truth_centre_y) ** 2)
            column.append(L2_distance)
        result.append(column)
    return np.array(result, np.float32)

def calc_IOU(box1: BoundingBox, box2: BoundingBox) -> float:
    boxA = [box1.x, box1.y, box1.x + box1.width, box1.y + box1.height]
    boxB = [box2.x, box2.y, box2.x + box2.width, box2.y + box2.height]
    # Taken from https://www.pyimagesearch.com/2016/11/07/intersection-over-union-iou-for-object-detection/
    # determine the (x, y)-coordinates of the intersection rectangle
    xA = max(boxA[0], boxB[0])
    yA = max(boxA[1], boxB[1])
    xB = min(boxA[2], boxB[2])
    yB = min(boxA[3], boxB[3])
    # compute the area of intersection rectangle
    interArea = max(0, xB - xA + 1) * max(0, yB - yA + 1)
    # compute the area of both the prediction and ground-truth
    # rectangles
    boxAArea = (boxA[2] - boxA[0] + 1) * (boxA[3] - boxA[1] + 1)
    boxBArea = (boxB[2] - boxB[0] + 1) * (boxB[3] - boxB[1] + 1)
    # compute the intersection over union by taking the intersection
    # area and dividing it by the sum of prediction + ground-truth
    # areas - the interesection area
    iou = interArea / float(boxAArea + boxBArea - interArea)
    # return the intersection over union value
    return iou

def calc_confusion_matrix_class(
    predictions: list[BoundingBox],
    ground_truth: list[BoundingBox],
    IOU_threshold: float
) -> tuple[int, int, int]:
    true_positive = 0
    false_positive = 0
    false_negative = 0
    pred_copy = predictions[:]
    truth_copy = ground_truth[:]
    
    while (pred_copy and truth_copy):
        costs = calc_L2_matrix(pred_copy, truth_copy)
        row_ids, col_ids = lapsolver.solve_dense(costs)
        cols_to_remove = []
        for row, col in zip(row_ids, col_ids):
            IOU = calc_IOU(pred_copy[row], truth_copy[col])
            if IOU >= IOU_threshold:
                true_positive += 1
                cols_to_remove.append(col)
            else:
                false_positive += 1
        helpers.delete_multiple_elements(pred_copy, row_ids)
        helpers.delete_multiple_elements(truth_copy, cols_to_remove)
    false_positive += len(pred_copy)
    false_negative += len(truth_copy)

    return true_positive, false_positive, false_negative

def build_index_refs(input: list[BoundingBox]) -> dict[int, int]:
    result = {}
    for i, entry in enumerate(input):
        if entry.parent:
            result[i] = input.index(entry.parent)
    return result

def calc_confusion_matrix_references(
    predictions: list[BoundingBox],
    ground_truth: list[BoundingBox]
) -> tuple[int, int, int]:
    true_positive = 0
    false_positive = 0
    false_negative = 0
    prediction_deps = build_index_refs(predictions)
    truth_deps = build_index_refs(ground_truth)
    costs = calc_L2_matrix(predictions, ground_truth)
    row_ids, col_ids = lapsolver.solve_dense(costs)
    pred_truth_map = {row:col for row, col in zip(row_ids, col_ids)}

    for child, parent in prediction_deps.items():
        if (child in pred_truth_map.keys() and parent in pred_truth_map.keys()):
            gt_child = pred_truth_map[child]
            gt_parent = pred_truth_map[parent]

            if (gt_child in truth_deps.keys() and gt_parent == truth_deps[gt_child]):
                true_positive += 1
            else:
                false_positive +=1
        else:
            false_positive +=1
    
    false_negative += max(0, len(truth_deps) - len(prediction_deps))

    return true_positive, false_positive, false_negative

def evaluate(
    predictions: list[BoundingBox],
    ground_truth: list[BoundingBox],
    IOU_threshold: float = IOU_THRESHOLD,
    eval_dependencies: bool = True,
    classes=[t.value for t in TargetType]
) -> dict[str, tuple[int, int, int]]:
    result = {}
    for cls in classes:
        pred_filtered = [pred for pred in predictions if pred.type == cls]
        gt_filtered = [gt for gt in ground_truth if gt.type == cls]
        tmp_res = calc_confusion_matrix_class(pred_filtered, gt_filtered, IOU_threshold)
        result[cls] = tmp_res
    
    if eval_dependencies:
        result['_references'] = calc_confusion_matrix_references(predictions, ground_truth) 

    return result



sci_parser = SciAnnotParser()
res1 = sci_parser.parse_text(sci_annot_json_text_1)
res2 = sci_parser.parse_text(sci_annot_json_text_2)

print(evaluate(res2, res1))