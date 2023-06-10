import argparse
from sci_annot_eval.common.bounding_box import AbsoluteBoundingBox, RelativeBoundingBox

from sci_annot_eval.exporters.sci_annot_exporter import SciAnnotExporter
from . helpers import rasterize_pdfs, pdffigures2_page_splitter, deepfigures_prediction
import coloredlogs
import logging
from enum import Enum
from . benchmarking import benchmark
from . parsers import sci_annot_parser, pdffigures2_parser, parserInterface
from sci_annot_eval.common.prediction_field_mapper import Pdffigures2FieldMapper, DeepfiguresFieldMapper
import os
import pandas as pd

# TODO: Type hint values
class RegisteredParsers(Enum):
    SCI_ANNOT = sci_annot_parser.SciAnnotParser()
    PDF_FIGURES_2 = pdffigures2_parser.PdfFigures2Parser(Pdffigures2FieldMapper)
    DEEPFIGURES = pdffigures2_parser.PdfFigures2Parser(DeepfiguresFieldMapper)

def run_benchmark(
    render_summary_parquet_path: str,
    gtruth_parser_name: str,
    pred_parser_name: str,
    gtruth_dir: str,
    pred_dir: str,
    output_parquet_path: str,
    IOU_threshold: float = 0.8,
    **kwargs
):  
    gtruth_parser = RegisteredParsers.__getitem__(gtruth_parser_name)
    pred_parser = RegisteredParsers.__getitem__(pred_parser_name)

    benchmark(
        render_summary_parquet_path,
        gtruth_parser.value,
        pred_parser.value,
        gtruth_dir,
        pred_dir,
        output_parquet_path,
        IOU_threshold
    )

def run_deepfigures_prediction(
    deepfigures_root: str,
    input_folder: str,
    output_folder: str,
    run_summary_csv_path: str,
    **kwargs
):
    deepfigures_prediction.run_deepfigures_prediction_for_folder(
        deepfigures_root,
        input_folder,
        output_folder,
        run_summary_csv_path
    )

def run_transpile(
    input_dir: str,
    input_parser_name: str,
    render_summary_parquet_path: str,
    output_dir: str,
    **kwargs
):
    input_parser = RegisteredParsers.__getitem__(input_parser_name).value
    exporter = SciAnnotExporter()
    if not os.path.exists(output_dir):
        logging.debug('Output directory does not exist. Creating it...')
        os.mkdir(output_dir)

    files = os.listdir(input_dir)
    render_summ = pd.read_parquet(render_summary_parquet_path)

    for i, file in enumerate(files):
        id = file[:-5]
        logging.debug(f'Transpiling file {i+1}/{len(files)} with id {id}')
        summary_row = render_summ[render_summ.index == id]
        relative_input = input_parser.parse_file_relative(os.path.join(input_dir, file)) 
        exporter.export_to_file(
            relative_input, 
            int(summary_row.width.values[0]),
            int(summary_row.height.values[0]),
            os.path.join(output_dir, file)
        )
    
    logging.info(f'Transpiled {len(files)} files')


# TODO: Make args consistent
def main():
    parser = argparse.ArgumentParser(description='Command line tool for managing the sci_annot evaluator and its helper functions', argument_default=argparse.SUPPRESS)
    parser.add_argument('--verbose', '-v', dest='verbose', help='Enable verbose logging (info, debug)', action='count', default=0)
    subparsers = parser.add_subparsers()

    parser_rasterize = subparsers.add_parser(
        'rasterize',
        description='Rasterize all pdfs in input folder and additionally produce a summary parquet file called render_summary.parquet in the output folder.',
        argument_default=argparse.SUPPRESS
    )
    parser_rasterize.add_argument('-i', dest='input-dir', metavar='input_folder', help='Input folder containing PDFs.', required=True)
    parser_rasterize.add_argument('-o' ,dest='output-dir', metavar='output_folder', help='Output folder to save page rasters.', required=True)
    parser_rasterize.add_argument('--dpi', metavar='DPI', help='DPI to render at (default is 150).', type=int)
    parser_rasterize.add_argument('-f', dest='format', metavar='format', help='Output format for images (default is png).')
    parser_rasterize.add_argument('-t', dest='nr-threads', metavar='threads', help='Number of threads to use when rasterizing (default is 8).')
    parser_rasterize.set_defaults(func=rasterize_pdfs.rasterize)

    parser_pdffig2 = subparsers.add_parser(
        'split-pdffigures2',
        description='Take original pdffigures2 output and split it into validator-friendly per-page files.',
        argument_default=argparse.SUPPRESS
    )
    parser_pdffig2.add_argument('-i', dest='input-dir', metavar='input_folder', help='Input folder containing the original predictions.', required=True)
    parser_pdffig2.add_argument('-o' ,dest='output-dir', metavar='output_folder', help='Output folder to save per-page predictions.', required=True)
    parser_pdffig2.add_argument('-p' ,dest='run-prefix', metavar='prefix', help='Prediction prefix specified with -d when running pdffigures2', required=True)
    parser_pdffig2.add_argument('-s' ,dest='render_summary_path', metavar='path', help='Path to render summary parquet file', required=True)
    parser_pdffig2.set_defaults(func=pdffigures2_page_splitter.split_pages)

    parser_benchmark = subparsers.add_parser(
        'benchmark',
        description='Evaluate predictions against a ground truth and produce TP, FP, and FN metrics for each page',
        argument_default=argparse.SUPPRESS
    )
    parser_benchmark.add_argument('-g', '--ground-truth-dir', dest='gtruth_dir', metavar='DIR', help='Directory containing files with ground truth annotations. Each should be named like PDF_ID-PAGENR.EXTENSION.', required=True)
    parser_benchmark.add_argument('-p', '--predictions-dir', dest='pred_dir', metavar='DIR', help='Directory containing files with prediction annotations. Each should be named like: PDF_ID-PAGENR.EXTENSION.', required=True)
    parser_benchmark.add_argument('-G', '--ground-truth-parser', dest='gtruth_parser_name', help='Parser to use for each file in the ground truth directory.', choices=RegisteredParsers.__members__, required=True)
    parser_benchmark.add_argument('-P', '--predictions-parser', dest='pred_parser_name', help='Parser to use for each file in the parser directory.', choices=RegisteredParsers.__members__, required=True)
    parser_benchmark.add_argument('-r', '--render-summary', dest='render_summary_parquet_path', metavar='PATH', help='Path to render_summary.parquet. This table contains all of the pages to test on.', required=True)
    parser_benchmark.add_argument('-o', '--output-path', dest='output_parquet_path', metavar='PATH', help='Tells the tool where to create a parquet file which contains the benchmark output', required=True)
    parser_benchmark.add_argument('-t', '--IOU-threshold', dest='IOU_threshold', metavar='THRESHOLD', help='Area under curve threshold over which annotations count as valid (default is 0.8)', type=float)
    parser_benchmark.set_defaults(func= run_benchmark)

    parser_deepfigures_predict = subparsers.add_parser(
        'deepfigures-predict',
        description='Use deepfigures to detect elements from each pdf in the input folder',
        argument_default=argparse.SUPPRESS
    )
    parser_deepfigures_predict.add_argument('deepfigures_root', metavar='DIR', help='Folder containing manage.py and all other requirements for deepfigures-open')
    parser_deepfigures_predict.add_argument('input_folder', metavar='DIR', help='Folder containing input PDFs')
    parser_deepfigures_predict.add_argument('output_folder', metavar='DIR', help='Folder in which predictions should be saved')
    parser_deepfigures_predict.add_argument('run_summary_csv_path', metavar='FILE', help='Path to save run information')
    parser_deepfigures_predict.set_defaults(func=run_deepfigures_prediction)

    parser_transpile = subparsers.add_parser(
        'transpile',
        description='Take a folder of predictions in one format and output them in another',
        argument_default=argparse.SUPPRESS
    )
    parser_transpile.add_argument('-i', '--input-dir', dest='input_dir', metavar='DIR', help='Directory containing files with prediction annotations. Each should be named like: PDF_ID-PAGENR.EXTENSION.', required=True)
    parser_transpile.add_argument('-I', '--input-parser', dest='input_parser_name', help='Parser to use for each file in the input directory.', choices=RegisteredParsers.__members__, required=True)
    parser_transpile.add_argument('-o', '--output-dir', dest='output_dir', metavar='PATH', help='Where to create the transpiled files', required=True)
    parser_transpile.add_argument('-r', '--render-summary', dest='render_summary_parquet_path', metavar='PATH', help='Path to render_summary.parquet. This is required in order to create right absolute coordinates', required=True)
    parser_transpile.set_defaults(func=run_transpile)

    args = parser.parse_args()
    logging_config = {"fmt":'%(asctime)s %(levelname)s: %(message)s', "level": logging.WARNING}
    if(args.verbose == 1):
        logging_config['level'] = logging.INFO
    elif(args.verbose == 2):
        logging_config['level'] = logging.DEBUG
    coloredlogs.install(**logging_config)
    logging.debug('DEBUG LOGGING ENABLED')
    logging.info('INFO LOGGING ENABLED')

    if hasattr(args, 'func'):
        args.func(**vars(args))

if __name__ == '__main__':
    main()
