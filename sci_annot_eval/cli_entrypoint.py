import argparse
from . helpers import rasterize_pdfs, pdffigures2_page_splitter
import coloredlogs
import logging

def main():
    parser = argparse.ArgumentParser(description='Command line tool for managing the sci_annot evaluator and its helper functions', argument_default=argparse.SUPPRESS)
    parser.add_argument('--verbose', '-v', dest='verbose', help='Enable verbose logging (info, debug)', action='count', default=0)
    subparsers = parser.add_subparsers()

    parser_rasterize = subparsers.add_parser(
        'rasterize',
        description='Rasterize all pdfs in input folder and additionally produce a summary parquet file called render_summary.parquet in the output folder.',
        argument_default=argparse.SUPPRESS
    )
    parser_rasterize.add_argument('-i', dest='input_dir', metavar='input_folder', help='Input folder containing PDFs.', required=True)
    parser_rasterize.add_argument('-o' ,dest='output_dir', metavar='output_folder', help='Output folder to save page rasters.', required=True)
    parser_rasterize.add_argument('--dpi', metavar='DPI', help='DPI to render at (default is 150).', type=int)
    parser_rasterize.add_argument('-f', dest='format', metavar='format', help='Output format for images (default is png).')
    parser_rasterize.add_argument('-t', dest='nr_threads', metavar='threads', help='Number of threads to use when rasterizing (default is 8).')
    parser_rasterize.set_defaults(func=rasterize_pdfs.rasterize)

    parser_pdffig2 = subparsers.add_parser(
        'split-pdffigures2',
        description='Take original pdffigures2 output and split it into validator-friendly per-page files.',
        argument_default=argparse.SUPPRESS
    )
    parser_pdffig2.add_argument('-i', dest='input_dir', metavar='input_folder', help='Input folder containing the original predictions.', required=True)
    parser_pdffig2.add_argument('-o' ,dest='output_dir', metavar='output_folder', help='Output folder to save per-page predictions.', required=True)
    parser_pdffig2.add_argument('-p' ,dest='run_prefix', metavar='prefix', help='Prediction prefix specified with -d when running pdffigures2', required=True)
    parser_pdffig2.add_argument('-s' ,dest='render_summary_path', metavar='path', help='Path to render summary parquet file', required=True)
    parser_pdffig2.set_defaults(func=pdffigures2_page_splitter.split_pages)


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
