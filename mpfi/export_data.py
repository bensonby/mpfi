import os
from pathlib import Path
import numpy as np
from .load_data import (
    _load_config,
)

def _get_mpf_columns(df, opt, config):
    columns = [
        c for c in list(df.columns)
        if c[0] != '_' and c.upper() == c
    ]
    if not opt['split_into_prod']:
        columns = [config['PROD_NAME_COLUMN']] + columns
    columns.extend(c for c in opt['include_columns'] if c not in columns) # to preserve order
    columns = [c for c in columns if c not in opt['exclude_columns']]
    return columns

def _to_prophet_type(dtype, series):
    if dtype in ['int', 'int32', 'Int32', 'int64']:
        return 'I'
    if dtype in ['float', 'float64']:
        return 'N'
    if dtype in [np.dtype('object'), 'str', 'string', 'category', 'object']:
        return 'T{}'.format(series.str.len().max())
    raise Exception('Unhandled dtype: {}, type is {}'.format(dtype, type(dtype)))

def _get_column_types(df, column_names):
    return [_to_prophet_type(df[c].dtype, df[c]) for c in column_names]

def export(data, folder, options={}, to_csv_options={}):
    default_options = {
        'split_into_prod': True,
        'write_header': True,
        'include_columns': [],
        'exclude_columns': [],
    }
    opt = {**default_options, **options}
    config = _load_config()
    df = data.reset_index()
    mpf_columns = _get_mpf_columns(df, opt, config)
    column_types = _get_column_types(df, mpf_columns)

    to_csv_opt = {
        'index': False,
        'columns': mpf_columns,
        'lineterminator': '\n',
        **to_csv_options,
    }

    if opt['split_into_prod']:
        try_folder = Path(folder)
        if try_folder.exists():
            response = input('Warning: folder "{}" already existed. Confirm overwrite? (y/n) '.format(folder))
            if not (response == 'Y' or response == 'y'):
                return
        else:
            os.mkdir(folder)
        for prod_name, rows in df.groupby(config['PROD_NAME_COLUMN']):
            filename = '{}/{}.{}'.format(folder, prod_name, config['MPF_EXTENSION'])
            with open(filename, 'w') as file_buffer:
                if opt['write_header']:
                    file_buffer.write('OUTPUT_FORMAT, mpfi\n')
                    file_buffer.write('NUMLINES, {}\n'.format(len(rows)))
                    file_buffer.write('VARIABLE_TYPES,{}\n'.format(','.join(column_types)))
                rows.to_csv(
                    file_buffer,
                    **to_csv_opt,
                )
        return

    # output to one single file
    filename = '{}.{}'.format(folder, config['MPF_EXTENSION'])
    try_file = Path(filename)
    if try_file.exists():
        response = input('Warning: file already existed. ({}) Confirm overwrite? (y/n) '.format(filename))
        if not (response == 'Y' or response == 'y'):
            return
    df.to_csv(
        filename,
        **to_csv_opt,
    )
