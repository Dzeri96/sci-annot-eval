import os
import logging
from collections import Counter
import pandas as pd
import subprocess
import shutil

def run_deepfigures_prediction_for_folder(
    deepfigures_root: str,
    input_folder: str,
    output_folder: str,
    run_summary_csv_path: str
):
    input_folder = os.path.abspath(input_folder)
    output_folder = os.path.abspath(output_folder)

    pdfs = [file for file in os.listdir(input_folder) if file.endswith('.pdf')]
    logging.info(f'Found {len(pdfs)} pdf files in {input_folder}')

    pdf_ids = set([file[:-4] for file in pdfs])
    existing_prediction_folders = set(os.listdir(output_folder))
    not_predicted_ids = pdf_ids - existing_prediction_folders
    logging.info(f'{len(not_predicted_ids)} have not been processed yet')

    id_status_dict = {}
    for i, id in enumerate(not_predicted_ids):
        logging.info(f'{i+1}/{len(not_predicted_ids)} Processing pdf {id}')
        output_dir_for_pdf = os.path.join(output_folder, id)
        os.mkdir(output_dir_for_pdf)
        with open(os.path.join(output_dir_for_pdf, 'log.txt'), 'w') as logfile:
            child = subprocess.Popen(
                args=['pipenv', 'run', 'python3', './manage.py', 'detectfigures', '-s', output_dir_for_pdf, os.path.join(input_folder, id + '.pdf')],
                cwd=deepfigures_root,
                stdout=logfile,
                stderr=logfile
            )
            streamdata = child.communicate()[0]
            return_code = child.returncode
        
        successful = return_code == 0
        if not successful:
            logging.error('Prediction unsuccessful!')
        else:
            # Delete rendered pages
            result_folder = os.path.join(output_folder, id, get_weird_output_folder(output_folder, id))
            rendered_folder = os.path.join(result_folder, id + '.pdf-images')
            shutil.rmtree(rendered_folder)
        id_status_dict[id] = successful
    
    logging.info(f'Successful counts: {Counter(id_status_dict.values())}')
    summary_series = pd.Series(id_status_dict, name='prediction_successful')
    summary_series.to_csv(run_summary_csv_path, index_label='pdf_id')

    logging.debug('Extracting result JSONs')
    os.mkdir(os.path.join(output_folder, 'results'))
    for id, successful in id_status_dict.items():
        if successful:
            result_folder = os.path.join(output_folder, id, get_weird_output_folder(output_folder, id))
            shutil.copy(
                os.path.join(result_folder, id + 'deepfigures-results.json'),
                os.path.join(output_folder, 'results', id + '.json'),
            )

def get_weird_output_folder(output_root: str, pdf_id: str)-> str:
    all_entries = os.listdir(os.path.join(output_root, pdf_id))
    log_txt_excluded_entries = [entry for entry in all_entries if entry != 'log.txt']
    # Yeah I know it's ugly
    return log_txt_excluded_entries[0]
    

