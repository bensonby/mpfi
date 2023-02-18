import re
import pandas as pd
import numpy as np

'''
data: pandas DataFrame
key_tuple: a tuple which is the "index_col" of the data
'''
def is_exist(data, key_tuple):
    return data.index.isin([key_tuple]).any()

def get_index_values(data, column):
    return data.index.get_level_values(column)

'''
find header row of a .fac or a model point file (the row starting with !)
zero-indexed, i.e. if the header is at the first row, it will return 0
'''
def find_fac_header_row(filename):
    result = 0
    # strange characters.. need to set encoding
    with open(filename, 'r', encoding='latin-1') as f:
        for line in f:
            if line[0] == '!':
                return result
            result += 1

def get_meta(filename):
    result = {
        'header_row': -1,
        'rows': 0,
        'column_specs': {},
        'date_columns': [],
    }
    variable_types = None
    numlines = -1
    current_line = -1
    passed_content = False
    with open(filename, 'r', encoding='latin-1') as f:
        for line in f:
            current_line = current_line + 1
            matching_numlines = re.match(r"^NUMLINES,[\s]*([\d]+)", line)
            matching_formats = re.match(r"^VARIABLE_TYPES,", line)
            if matching_numlines is not None:
                numlines = int(matching_numlines[1])
            elif matching_formats is not None:
                variable_types = line.strip().split(',')[1:] # first column is VARIABLE_TYPES, not used
            elif not passed_content and (line[0] == '!' or line[0] == '&'):
                result['header_row'] = current_line # zero-based
                variable_names = line.strip().split(',')
            elif line[0] == '*':
                passed_content = True
                result['rows'] = result['rows'] + 1

    if result['header_row'] == -1 or result['rows'] == 0:
        print('Malformed model point file format in: ' + filename)
        raise ValueError

    if numlines != -1 and numlines != result['rows']:
        print('Warning: actual lines loaded ({}) different from NUMLINES shown in model point ({}) in: {}'.format(result['rows'], numlines, filename))

    # set formats
    if variable_types is not None:
        if len(variable_types) != len(variable_names):
            print('Malformed model point file (variable_types) -- number of columns not matched')
            raise ValueError
        result['column_specs'] = dict([
            (
                variable_names[i],
                {
                    'V': pd.CategoricalDtype(['*']), # for ! column with VARIABLE_TYPES
                    'T': np.dtype('str'),
                    'I': pd.Int32Dtype(),
                    'S': pd.Int16Dtype(),
                    'N': np.float64,
                }[variable_types[i][0]],
            ) for i in range(0, len(variable_types))
            if variable_types[i][0] != 'D'
        ])
        result['date_columns'] = [
            variable_names[i]
            for i in range(0, len(variable_types))
            if variable_types[i][0] == 'D'
        ]
    return result
