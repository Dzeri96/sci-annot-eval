import pandas as pd
import os

from sci_annot_eval.common.bounding_box import AbsoluteBoundingBox, RelativeBoundingBox
from . parsers.parserInterface import Parser
from sci_annot_eval import evaluation

def build_id_file_dict(path: str):
    result = {}
    for file in os.listdir(path):
        no_extension = file.split('.')[0]
        result[no_extension] = os.path.join(path, file)

    return result

def build_3D_dict(input: dict):
    """
        Converts the nested dictionary into an input for pandas' multiIndex.
        See https://stackoverflow.com/questions/24988131/nested-dictionary-to-multiindex-dataframe-where-dictionary-keys-are-column-label
    """
    return {
        (outerKey, innerKey): values 
        for outerKey, innerDict in input.items() 
        for innerKey, values in innerDict.items()
    }

def benchmark(
    render_summary_parquet_path: str,
    gtruth_parser: Parser,
    pred_parser: Parser,
    gtruth_dir: str,
    pred_dir: str,
    output_parquet_path: str,
    IOU_threshold: float = 0.8
):
    result_dict = {}
    gtruth_file_dict = build_id_file_dict(gtruth_dir)
    pred_file_dict = build_id_file_dict(pred_dir)

    render_summ = pd.read_parquet(render_summary_parquet_path)
    for row in render_summ.itertuples():
        id = row.Index
        ground_truth = []
        if id in gtruth_file_dict.keys():
            ground_truth = gtruth_parser.parse_file_relative(gtruth_file_dict[id])
        predictions = []
        if id in pred_file_dict.keys():
            predictions = pred_parser.parse_file_relative(pred_file_dict[id])

        result_dict[id] = evaluation.evaluate(predictions, ground_truth, IOU_threshold)

    """
        Produces a DF in this shape:
        class    class2          ... class_1                    ... 
        metric metric_1 metric_2 ... metric_1 metric_2 metric_3 ...
        id                                        
        id_1         -1       -2           1        2       2
        id_2         -3       -4           3        4       0
    """
    result_df = pd.DataFrame.from_dict(result_dict, orient='index').stack()
    result_df = pd.DataFrame(result_df.values.tolist(), index=result_df.index, columns=['TP', 'FP', 'FN'])\
        .unstack()\
        .swaplevel(axis=1)\
        .sort_index(axis=1, level=0)\
        .rename_axis(index='id', columns=['class', 'metric'])


    result_df.to_parquet(output_parquet_path)
        
