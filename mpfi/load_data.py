from pathlib import Path
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
CONFIG_FILE = 'mpfi_config.py'

def _load_config():
    try_file = Path(CONFIG_FILE)
    if try_file.exists():
        spec = importlib.util.spec_from_file_location('dummy-name',CONFIG_FILE)
        custom_config = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(custom_config)
        print('Config file {} found.'.format(CONFIG_FILE))
        return custom_config.config
    print('Config file {} not found in current directory. Falling back to default config.'.format(CONFIG_FILE))
    print('To generate a config file for further edit, run `mpfi.generate_config()`')
    return default_config

def generate_config():
    try_file = Path(CONFIG_FILE)
    if try_file.exists():
        print('Aborted. File {} already existed'.format(CONFIG_FILE))
    f = open(CONFIG_FILE, 'w')
    f.write(default_config_str)
    f.close()
    print('{} created. Please go ahead and edit the file.'.format(CONFIG_FILE))

def _get_files_from_folder(folder, file_pattern):
    return [Path(p) for p in glob(folder + file_pattern)]

def _read_single_mpf(config, full_filename, prod_name):
    if config['FILE_NAME_COLUMN']:
        extra_columns = {
            config['PROD_NAME_COLUMN']: prod_name,
            config['FILE_NAME_COLUMN']: full_filename,
        }
    else:
        extra_columns = {
            config['PROD_NAME_COLUMN']: prod_name,
        }
    meta = mpf_meta(full_filename)
    return pd.read_csv(
        full_filename,
        skiprows=meta['header_row'],
        dtype={**meta['column_specs'], **config['MPF_COLUMN_SPECS']},
        index_col=config['MPF_INDEX_COLUMNS'],
        error_bad_lines=False,
        nrows=meta['rows']
        ).dropna(how='all').assign(**extra_columns)

def _read_fac(full_filename):
    header_row = find_fac_header_row(full_filename)
    cols = pd.read_csv(
        full_filename,
        encoding='latin-1', # There are some strange characters in the start of .fac files..
        skiprows=header_row,
        nrows=1,
        ).columns
    first_column_type = {cols[0]: pd.CategoricalDtype(['*'])}
    key_column_count = int(cols[0][1:])
    return pd.read_csv(
        full_filename,
        encoding='latin-1', # There are some strange characters in the start of .fac files..
        skiprows=header_row,
        dtype=first_column_type,
        index_col=list(range(1, key_column_count)),
        ).dropna(how='all')

def _get_file_pattern(file_pattern):
    if file_pattern is None:
        return '*.' + config['MPF_EXTENSION']
    if type(file_pattern) is list:
        return file_pattern
    if type(file_pattern) is not str:
        print('Invalid file_pattern parameter. None, list or str is expected. {} given.'.format(type(file_pattern)))
        return None
    ext_pos = file_pattern.lower().find('.' + config['MPF_EXTENSION'].lower())
    if ext_pos == -1:
        return file_pattern + '.' + config['MPF_EXTENSION']
    return file_pattern

def _get_folder(folder_filter, folder=None):
    if folder is not None:
        return folder
    folder_name = None
    for path in config['MPF_FOLDERS']:
        if folder_filter is None:
            folder_name = path
            break
        if type(folder_filter) is list:
            str_list = folder_filter
        elif type(folder_filter) is not str:
            print('Invalid folder_filter parameter. None, list or str is expected. {} given.'.format(type(folder_filter)))
            return None
        else:
            str_list = [folder_filter]
        not_found = [1 for s in str_list if path.find(s) == -1]
        if len(not_found) > 0:
            continue
        folder_name = path
        break
    if folder_name is None:
        print('No folder matching the criteria is found. Your criteria:')
        print(folder_filter)
        print('Folders available (defined in {}): '.format(CONFIG_FILE))
        print(config['MPF_FOLDERS'])
        return None
    return folder_name

def load(file_pattern=None, folder_filter=None, folder=None):
    config = _load_config()
    file_pattern = _get_file_pattern(file_pattern)
    folder = _get_folder(folder_filter, folder)
    print('Reading from {}, file_pattern {}'.format(folder, file_pattern))
    files = _get_files_from_folder(folder, file_pattern)
    if len(files) == 0:
        print('No model point files match your selection criteria.')
        return
    df_from_each_file = (_read_single_mpf(config, str(f), f.stem) for f in files)
    concatenated_df = pd.concat(df_from_each_file, ignore_index=True)
    return concatenated_df

def load_fac(filename, folder=None):
    config = _load_config()
    if filename.find('.' + config['MPF_EXTENSION']) > -1:
        prod_name = filename[0:6]
    else:
        prod_name = filename
        filename = prod_name + '.' + config['MPF_EXTENSION']

    if folder is not None:
        full_filename = folder + filename
        return _read_fac(full_filename)

    for folder in config['FAC_FOLDERS']:
        full_filename = folder + filename
        try_file = Path(full_filename)
        if try_file.exists() and not try_file.is_dir():
            print('Reading from {}'.format(full_filename))
            return _read_fac(full_filename)

    print('fac file not found: {}'.format(filename))
    print('Folders available (defined in {}): '.format(CONFIG_FILE))
    print(config['FAC_FOLDERS'])
    return None
