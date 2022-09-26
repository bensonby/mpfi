from pathlib import Path, PurePath
from glob import glob
import importlib.util
import pandas as pd
from .util import (
    find_fac_header_row,
    mpf_meta,
)
from .config_default import (
    default_config,
    default_config_str,
)

def _load_config():
    try_file = Path('mpfi-config.py')
    if try_file.exists():
        spec = importlib.util.spec_from_file_location('dummy-name', 'mpfi-config.py')
        custom_config = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(custom_config)
        print('Config file mpfi-config.py found.')
        return custom_config.config
    print('Config file mpfi-config.py not found in current directory. Falling back to default config.')
    print('To generate a config file for further edit, run `mpfi.generate_config()`')
    return default_config

def generate_config():
    # TODO: check if file exist
    try_file = Path('mpfi-config.py')
    if try_file.exists():
        print('Aborted. File mpfi-config.py already existed')
    f = open('mpfi-config.py', 'w')
    f.write(default_config_str)
    f.close()
    print('mpfi-config.py created. Please go ahead and edit the file.')

def _get_files_from_folder(folder, file_pattern):
    return [Path(p) for p in glob(folder + file_pattern)]

def _read_single_mpf(config, full_filename, prod_name, read_csv_options={}):
    meta = mpf_meta(full_filename)
    options = {
        'skiprows': meta['header_row'],
        'dtype': {**meta['column_specs'], **config['MPF_COLUMN_SPECS']},
        'index_col': config['MPF_INDEX_COLUMNS'],
        'encoding': 'latin-1', # to prevent error while reading garbage footer lines
        'on_bad_lines': 'warn',
        'nrows': meta['rows'],
        **read_csv_options,
    }
    return pd.read_csv(full_filename, **options).dropna(how='all').assign(**{
        config['PROD_NAME_COLUMN']: prod_name,
        config['FILE_NAME_COLUMN']: full_filename,
    })

def _read_fac(full_filename, read_csv_options={}):
    header_row = find_fac_header_row(full_filename)
    options = {
        'encoding': 'latin-1', # There are some strange characters in the start of .fac files..
        'skiprows': header_row,
        'nrows': 1,
        **read_csv_options,
    }
    cols = pd.read_csv(full_filename, **options).columns
    first_column_type = {cols[0]: pd.CategoricalDtype(['*'])}
    key_column_count = int(cols[0][1:])
    options = {
        'encoding': 'latin-1', # There are some strange characters in the start of .fac files..
        'skiprows': header_row,
        'dtype': first_column_type,
        'index_col': list(range(1, key_column_count)),
        **read_csv_options,
    }
    return pd.read_csv(full_filename, **options).dropna(how='all')

def load_all(containing_text, file_pattern=None, read_csv_options={}):
    config = _load_config()
    if file_pattern is None:
        file_pattern = '*.' + config['MPF_EXTENSION']
    folder_name = None
    for folder in config['MPF_FOLDERS']:
        if containing_text is not None:
            if type(containing_text) is list:
                str_list = containing_text
            else:
                str_list = [containing_text]
            not_found = [1 for s in str_list if folder.find(s) == -1]
            if len(not_found) > 0:
                continue
            folder_name = folder
            break
    if folder_name is None:
        print('No folder matching the criteria is found. Your criteria:')
        print(containing_text)
        print('Folders available (defined in mpfi-config.py): ')
        print(config['MPF_FOLDERS'])
        return
    print('Reading from {}, file_pattern {}'.format(folder_name, file_pattern))
    files = _get_files_from_folder(folder_name, file_pattern)
    if len(files) == 0:
        print('No model point files match your selection criteria.')
        return
    df_from_each_file = (_read_single_mpf(config, str(f), f.stem, read_csv_options) for f in files)
    concatenated_df = pd.concat(df_from_each_file, ignore_index=True)
    return concatenated_df

'''
filename: allow either with .PRO or without; extension defined in mpfi-config.py
folder: to be read from .env
'''
def load(filename, containing_text=None, folder=None, read_csv_options={}):
    config = _load_config()
    ext_pos = filename.find('.' + config['MPF_EXTENSION'])
    if ext_pos > -1: # has extension specified
        prod_name = filename[0:ext_pos]
    else:
        prod_name = filename
        filename = prod_name + '.' + config['MPF_EXTENSION']

    if folder is not None:
        full_filename = str(PurePath(folder, filename))
        return _read_single_mpf(config, full_filename, prod_name, read_csv_options)

    for folder in config['MPF_FOLDERS']:
        full_filename = str(PurePath(folder, filename))
        if containing_text is not None:
            if type(containing_text) is list:
                str_list = containing_text
            else:
                str_list = [containing_text]
            not_found = [1 for s in str_list if full_filename.find(s) == -1]
            if len(not_found) > 0:
                continue
        try_file = Path(full_filename)
        if try_file.exists() and not try_file.is_dir():
            print('Reading from {}'.format(full_filename))
            return _read_single_mpf(config, full_filename, prod_name, read_csv_options)

    print('model point file not found: {}'.format(filename))
    print('Folders available (defined in mpfi-config.py): ')
    print(config['MPF_FOLDERS'])
    return None

def load_fac(filename, folder=None, read_csv_options={}):
    config = _load_config()
    if filename.find('.' + config['FAC_EXTENSION']) == -1:
        filename = filename + '.' + config['FAC_EXTENSION']

    if folder is not None:
        full_filename = PurePath(folder, filename)
        return _read_fac(full_filename, read_csv_options)

    for folder in config['FAC_FOLDERS']:
        full_filename = PurePath(folder, filename)
        try_file = Path(full_filename)
        if try_file.exists() and not try_file.is_dir():
            print('Reading from {}'.format(full_filename))
            return _read_fac(full_filename, read_csv_options)

    print('fac file not found: {}'.format(filename))
    print('Folders available (defined in mpfi-config.py): ')
    print(config['FAC_FOLDERS'])
    return None
