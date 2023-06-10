import logging
from . common.bounding_box import BoundingBox, TargetType, AbsoluteBoundingBox, RelativeBoundingBox
from . helpers import helpers
import math
import numpy as np
import lapsolver
from typing import Sequence

SCALE_FACTOR = 100
IOU_THRESHOLD = 0.8

def calc_L2_matrix(predictions: list[RelativeBoundingBox], ground_truth: list[RelativeBoundingBox]) -> np.ndarray:
    """
    Given a a list of predictions and ground truth annotations, produces a matrix in this form:
        [
            [gt0_pd0, gt0_pd1, gt0_pd2, ...],\n
            [gt1_pd0, gt1_pd1, gt1_pd2, ...],\n
            [gt2_pd0, gt2_pd1, gt2_pd2, ...]
        ]
    where gtX_pdY represents the distance between the center of ground truth bounding box X and prediction box Y.
    """
    result = []
    for prediction in predictions:
        if type(prediction) is not RelativeBoundingBox:
            raise TypeError(f'Annotation {prediction} is not of type RelativeBoundingBox!')
        pred_centre_x = (prediction.x + (prediction.width / 2)) * SCALE_FACTOR
        pred_centre_y = (prediction.y + (prediction.height / 2)) * SCALE_FACTOR
        column = []
        for truth in ground_truth:
            if type(truth) is not RelativeBoundingBox:
                raise TypeError(f'Annotation {truth} is not of type RelativeBoundingBox!')
            truth_centre_x = (truth.x + (truth.width / 2)) * SCALE_FACTOR
            truth_centre_y = (truth.y + (truth.height / 2)) * SCALE_FACTOR
            L2_distance = math.sqrt((pred_centre_x - truth_centre_x) ** 2 + (pred_centre_y - truth_centre_y) ** 2)
            column.append(L2_distance)
        result.append(column)
    return np.array(result, np.float32)

def calc_IOU(box1: RelativeBoundingBox, box2: RelativeBoundingBox) -> float:
    boxA = [box1.x, box1.y, box1.x + box1.width, box1.y + box1.height]
    boxA_scaled = [entry * SCALE_FACTOR for entry in boxA]
    boxB = [box2.x, box2.y, box2.x + box2.width, box2.y + box2.height]
    boxB_scaled = [entry * SCALE_FACTOR for entry in boxB]
    # Taken from https://www.pyimagesearch.com/2016/11/07/intersection-over-union-iou-for-object-detection/
    # determine the (x, y)-coordinates of the intersection rectangle
    xA = max(boxA_scaled[0], boxB_scaled[0])
    yA = max(boxA_scaled[1], boxB_scaled[1])
    xB = min(boxA_scaled[2], boxB_scaled[2])
    yB = min(boxA_scaled[3], boxB_scaled[3])
    # compute the area of intersection rectangle
    interArea = max(0, xB - xA + 1) * max(0, yB - yA + 1)
    # compute the area of both the prediction and ground-truth
    # rectangles
    boxAArea = (boxA_scaled[2] - boxA_scaled[0] + 1) * (boxA_scaled[3] - boxA_scaled[1] + 1)
    boxBArea = (boxB_scaled[2] - boxB_scaled[0] + 1) * (boxB_scaled[3] - boxB_scaled[1] + 1)
    # compute the intersection over union by taking the intersection
    # area and dividing it by the sum of prediction + ground-truth
    # areas - the interesection area
    iou = interArea / float(boxAArea + boxBArea - interArea)
    # return the intersection over union value
    logging.debug(f'{boxA_scaled=}, {boxB_scaled=}, {box1.type=}, {box2.type=}, {iou=}')
    return iou

def calc_confusion_matrix_class(
    predictions: list[RelativeBoundingBox],
    ground_truth: list[RelativeBoundingBox],
    IOU_threshold: float
) -> tuple[int, int, int]:
    """
    Runs the hungarian algorithm on two sets of bounding boxes and compares the IOU of matches.

    returns: (true positive, false_positive, false_negative) tuple.
    """
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

def build_index_refs(input: Sequence[BoundingBox]) -> dict[int, int]:
    """
    Builds a dictionary where the keys correspond to the indexes of the input array (representing children), and the values refer to the indexes of the input array referring to their parents.
    Simply put: {idx_child -> idx_parent}.
    """
    index_to_parent_map = {}
    for i, entry in enumerate(input):
        if entry.parent:
            index_to_parent_map[i] = input.index(entry.parent)
    return index_to_parent_map

def calc_confusion_matrix_references(
    predictions: list[RelativeBoundingBox],
    ground_truth: list[RelativeBoundingBox]
) -> tuple[int, int, int]:
    true_positive = 0
    false_positive = 0
    false_negative = 0
    prediction_deps = build_index_refs(predictions)
    truth_deps = build_index_refs(ground_truth)
    costs = calc_L2_matrix(predictions, ground_truth)
    if (predictions and ground_truth):
        row_ids, col_ids = lapsolver.solve_dense(costs)
        pred_truth_map = {row:col for row, col in zip(row_ids, col_ids)}
        for child, parent in prediction_deps.items():
            # Check if both parent and child have an entry in the assignment table
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
    else:
        # TODO: Check if this should be predictions or prediction_deps
        false_positive = len(prediction_deps)

    return true_positive, false_positive, false_negative

def evaluate(
    predictions: list[RelativeBoundingBox],
    ground_truth: list[RelativeBoundingBox],
    IOU_threshold: float = IOU_THRESHOLD,
    eval_dependencies: bool = True,
    classes=[t.value for t in TargetType] #type: ignore
) -> dict[str, tuple[int, int, int]]:
    """
        Returns dictionary with keys corresponding to classes (Figure, Table, etc., and possibly _references),
            where the values are tuples that have TP, FP, and FN values for a confusion matrix.
    """
    result = {}
    for cls in classes:
        pred_filtered = [pred for pred in predictions if pred.type == cls]
        gt_filtered = [gt for gt in ground_truth if gt.type == cls]
        tmp_res = calc_confusion_matrix_class(pred_filtered, gt_filtered, IOU_threshold)
        result[cls] = tmp_res
    
    if eval_dependencies:
        result['_references'] = calc_confusion_matrix_references(predictions, ground_truth) 

    return result

def check_no_disagreements(
    predictions: list[RelativeBoundingBox],
    ground_truth: list[RelativeBoundingBox],
    IOU_threshold: float = IOU_THRESHOLD
)-> bool:
    confusion_matrix = evaluate(predictions, ground_truth, IOU_threshold)
    logging.debug(f'{confusion_matrix=}')
    for _, fp, fn in confusion_matrix.values():
        if fp or fn:
            return False
    return True