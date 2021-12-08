import os
import time
import pandas as pd
from pdf2image import convert_from_path
from pdf2image.generators import threadsafe
from ..common import config
import logging

@threadsafe
def dummygenerator(name: str):
    while True:
        yield name

def rasterize(
    input_dir: str,
    output_dir: str,
    dpi: int= config.COMMON_DPI,
    format: str = config.OUTPUT_FORMAT,
    threads: int = 8,
    **kwargs):
    raw_files = [f for f in os.listdir(input_dir) if f.endswith('.pdf')]
    nr_files = len(raw_files)

    start = time.time()
    nr_pages = 0
    output_dict = {}
    for i, pdf in enumerate(raw_files):
        input_file = os.path.join(input_dir, pdf)
        output_file = pdf[:-4]
        logging.debug(f'Input: {input_file}')
        result = convert_from_path(
            input_file,
            output_folder=output_dir,
            fmt=format,
            output_file=dummygenerator(output_file),
            dpi=dpi,
            thread_count=threads
        )
        res_len = len(result)
        for j, page in enumerate(result):
            # To handle how pdf2ppm expands digits
            nr_digits = len(str(res_len))
            full_id = '%s-%0*d' % (output_file, nr_digits, j+1)
            output_dict[full_id] = [output_file, j+1, page.width, page.height, config.OUTPUT_FORMAT, config.COMMON_DPI]

        nr_pages += len(result)
        logging.info(f'Rasterized {i+1}/{nr_files} PDFs.')

    end = time.time()
    elapsed_time = end - start
    logging.info('Rasterized %d pages in %.3f minutes, at an avg. of %.3fs per page.' % (nr_pages, elapsed_time/60, elapsed_time/nr_pages))

    job_summary_df = pd.DataFrame.from_dict(output_dict, orient='index', columns=['file', 'page_nr', 'width', 'height', 'format', 'DPI'])
    job_summary_df.to_parquet(os.path.join(output_dir, 'render_summary.parquet'))
    
