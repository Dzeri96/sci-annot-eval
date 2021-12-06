import sys
import os
import time
import pandas as pd
from pdf2image import convert_from_path
from sci_annot_eval.common import config


def dummygenerator(name: str):
    yield name

if __name__ == '__main__':
    input_dir = sys.argv[1]
    output_dir = sys.argv[2]

    raw_files = [f for f in os.listdir(input_dir) if f.endswith('.pdf')]
    nr_files = len(raw_files)

    start = time.time()
    nr_pages = 0
    output_dict = {}
    for i, pdf in enumerate(raw_files):
        input_file = os.path.join(input_dir, pdf)
        output_file = pdf[:-4]
        print(f'Input: {input_file}')
        print(f'Output file: {output_file}')
        result = convert_from_path(
            input_file,
            output_folder=output_dir,
            fmt=config.OUTPUT_FORMAT,
            output_file=dummygenerator(output_file),
            dpi=config.COMMON_DPI
        )
        res_len = len(result)
        for i, page in enumerate(result):
            # To handle how pdf2ppm expands digits
            nr_digits = len(str(res_len))
            full_id = '%s-%0*d' % (output_file, nr_digits, i+1)
            output_dict[full_id] = [output_file, i+1, page.width, page.height, config.OUTPUT_FORMAT, config.COMMON_DPI]

        nr_pages += len(result)
        print(f'Rasterized {i+1}/{nr_files} PDFs.')

    end = time.time()
    elapsed_time = end - start
    print('Rasterized %d pages in %.3f minutes, at an avg. of %.3fs per page.' % (nr_pages, elapsed_time/60, elapsed_time/nr_pages))

    job_summary_df = pd.DataFrame.from_dict(output_dict, orient='index', columns=['file', 'page_nr', 'width', 'height', 'format', 'DPI'])
    job_summary_df.to_parquet(os.path.join(output_dir, 'render_summary.parquet'))
    
