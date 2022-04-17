import json
import os
from typing import Any
import pandas as pd
import logging
import numpy as np

# TODO: Assumed by pdffigures2 and cannot be changed, but should be changed for deepfigures to 100
ASSUMED_DPI = 100

def append_entry(result_dict: dict[int, Any], page_nr: int, category: str, entry: dict):
    if page_nr not in result_dict.keys():
        result_dict[page_nr] = {'figures': [], 'regionless-captions': []}
    
    result_dict[page_nr][category].append(entry)

def split_pages(input_dir: str, output_dir: str, run_prefix: str, render_summary_path: str, **kwargs):
    """
        Turn the normal pdffigures2/deepfigures output into per-page output with width/height info.
        IMPORTANT: run pdffigures2 with the -c flag!

        run_prefix: str - Pandatory prefix that each json file contains,
            specified with the -d flag when running pdffigures2.

        render_summary_path: str - Path to the parquet file that contains information on rendered pages,
            like width, height, DPI etc.
            This is used to figure out which size the page would have, rendered at 72 DPI.
    """

    render_summ = pd.read_parquet(render_summary_path)
    input_files = [f for f in os.listdir(input_dir) if f.endswith('.json') and f.startswith(run_prefix)]
    if not os.path.exists(output_dir):
        logging.debug(f'Creating output dir {output_dir}')
        os.makedirs(output_dir)

    logging.info(f'Parsing {len(input_files)} files...')
    logging_points = list(np.linspace(len(input_files), 1, 10, dtype=np.int64))
    for file_nr, file in enumerate(input_files):
        full_input_file_path = os.path.join(input_dir, file)
        with open(full_input_file_path, 'r') as fp:
            result: dict[int, Any] = {}
            pdf_id = file[len(run_prefix):-5]
            parsed_json = json.load(fp)

        for figure_entry in parsed_json['figures']:
            # Pages are 0-indexed!
            append_entry(result, figure_entry['page']+1, 'figures', figure_entry)
        
        if 'regionless-captions' in parsed_json:
            for reg_cap_entry in parsed_json['regionless-captions']:
                # Pages are 0-indexed!
                append_entry(result, reg_cap_entry['page']+1, 'regionless-captions', reg_cap_entry)

        if result:
            rel_summs = render_summ[render_summ['file'] == pdf_id]
            for page_nr, entry_dict in result.items():
                summary_row = rel_summs[rel_summs['page_nr'] == page_nr].iloc[0]
                scale_factor = ASSUMED_DPI / summary_row['DPI']
                scaled_width = scale_factor * summary_row['width']
                scaled_height = scale_factor * summary_row['height']

                extended_entry = {'width': scaled_width, 'height': scaled_height, **entry_dict}
                with open(os.path.join(output_dir, str(summary_row.name)+'.json'), 'w+') as of:
                    json.dump(extended_entry, of, indent=4)
                    
        if file_nr+1 == logging_points[-1]:
            logging_points.pop()
            logging.info(f'Processed {file_nr+1}/{len(input_files)} files.')