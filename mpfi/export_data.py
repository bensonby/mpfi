import os
import re
import csv
from pathlib import Path
import numpy as np
from .load_data import (
    _load_config,
)

def _remove_asterisk_quotes(s):
    # replace "*" by * for start of data lines in MPF
    return re.sub(r'^"\*"', '*', s, flags=re.M)

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

def _to_prophet_type(dtype, series, date_format):
    dtype_str = str(dtype).lower()
    if dtype_str in ['int16']:
        return 'S'
    if dtype_str in ['int', 'int32', 'int64']:
        return 'I'
    if dtype_str in ['float', 'float64']:
        return 'N'
    if dtype_str in ['str', 'string', 'category', 'object']:
        length = int(series.str.len().max())
        return f'T{length}'
    if dtype_str in ['datetime64[ns]']:
        return f'D{date_format}'
    raise Exception('Unhandled dtype: {}, type is {}'.format(dtype, type(dtype)))

def _get_column_types(df, column_names, date_format):
    return [_to_prophet_type(df[c].dtype, df[c], date_format) for c in column_names]

def export(data, folder, options={}, to_csv_options={}):
    default_options = {
        'split_into_prod': True,
        'write_header': True,
        'include_columns': [],
        'exclude_columns': [],
        'output_format': 'mpfi',
    }
    opt = {**default_options, **options}
    config = _load_config()
    df = data.reset_index()
    mpf_columns = _get_mpf_columns(df, opt, config)

    to_csv_opt = {
        'index': False,
        'columns': mpf_columns,
        'lineterminator': '\n',
        'header': False,
        'quoting': csv.QUOTE_NONNUMERIC,
        'date_format': '%m/%d/%Y',
        **to_csv_options,
    }

    column_types = _get_column_types(df, mpf_columns, to_csv_opt['date_format'])

    if opt['split_into_prod']:
        try_folder = Path(folder)
        if try_folder.exists():
            response = input('Warning: folder "{}" already existed. Confirm overwrite? (y/n) '.format(folder))
            if not (response == 'Y' or response == 'y'):
                return
        else:
            os.mkdir(folder)
        for prod_name, rows in df.groupby(config['PROD_NAME_COLUMN']):
            out_lines = []
            if opt['write_header']:
                out_lines.append(f'OUTPUT_FORMAT, {opt["output_format"]}')
                out_lines.append(f'NUMLINES, {len(rows)}')
                types = ','.join(column_types)
                out_lines.append(f'VARIABLE_TYPES,{types}')
            out_lines.append(','.join(mpf_columns))
            data_lines = _remove_asterisk_quotes(
                rows.sort_values(['SPCODE'], kind='mergesort').to_csv(**to_csv_opt)
            )
            out_lines.append(data_lines)

            filename = '{}/{}.{}'.format(folder, prod_name, config['MPF_EXTENSION'])
            with open(filename, 'w', newline='\r\n') as f:
                for l in out_lines:
                    f.write(l + '\n')
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
