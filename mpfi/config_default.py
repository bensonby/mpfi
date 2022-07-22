import pandas as pd

default_config = {
    'MPF_FOLDERS': [
        # MPF file will be found in this order of paths, with trailing slash
        # The first one found will be used
        # Can be defined as relative path or absolute path
        # backslash in path needs to be entered by using two backslashes, alternatively a single slash "/" works too
        '.\\', # a dot means the same folder
        'MPFILES\\',
        'mpf/',
        'C:/users/abc/Downloads/mpf/', # Absolute path example
        'example/',
    ],

    'FAC_FOLDERS': [
      './',
      'TABLES/',
      'example/',
    ],

    'MPF_EXTENSION': 'PRO', # without the dot
    'FAC_EXTENSION': 'fac', # without the dot

    'PROD_NAME_COLUMN': '_PROD_NAME', # name of the additional column used for storing the MPF filename
    'FILE_NAME_COLUMN': '_FILE_NAME', # name of the additional column used for storing the full file path

    'MPF_COLUMN_SPECS': {
        # these will be used to override any column types specified in the MPF
        # column types are specified in the line above the headers in MPF
        # T for string, N for number, I for integer
        '!': pd.CategoricalDtype(['*']), # keep this line! as 1st column and for dropna to work
        'SPCODE': pd.Int32Dtype(),
        'POLICY_NUMBER': 'string',
        'PLAN_CODE': 'string',
        'AGE_AT_ENTRY': pd.Int32Dtype(),
        'DURATIONIF_M': pd.Int32Dtype(),
        'EFF_YEAR': pd.Int32Dtype(),
        'EFF_MONTH': pd.Int32Dtype(),
        'EFF_DAY': pd.Int32Dtype(),
        'POL_TERM_Y': pd.Int32Dtype(),
        'PREM_FREQ': pd.Int32Dtype(),
        'PREM_PAYBL_M': pd.Int32Dtype(),
    },

    'MPF_INDEX_COLUMNS': [
        # Insert the column names you wish to be the index, e.g. POL_NUMBER, SPCODE
    ],
}

default_config_str = '''import pandas as pd

config = {
    'MPF_FOLDERS': [
        # MPF file will be found in this order of paths, with trailing slash
        # The first one found will be used
        # Can be defined as relative path or absolute path
        # backslash in path needs to be entered by using two backslashes, alternatively a single slash "/" works too
        '.\\\\', # a dot means the same folder
        'MPFILES\\\\',
        'mpf/',
        'C:/users/abc/Downloads/mpf/', # Absolute path example
        'example/',
    ],

    'FAC_FOLDERS': [
      './',
      'TABLES/',
      'example/',
    ],

    'MPF_EXTENSION': 'PRO', # without the dot
    'FAC_EXTENSION': 'fac', # without the dot

    'PROD_NAME_COLUMN': '_PROD_NAME', # name of the additional column used for storing the MPF filename
    'FILE_NAME_COLUMN': '_FILE_NAME', # name of the additional column used for storing the full file path

    'MPF_COLUMN_SPECS': {
        # these will be used to override any column types specified in the MPF
        # column types are specified in the line above the headers in MPF
        # T for string, N for number, I for integer
        '!': pd.CategoricalDtype(['*']), # keep this line! as 1st column and for dropna to work
        'SPCODE': pd.Int32Dtype(),
        'POLICY_NUMBER': 'string',
        'PLAN_CODE': 'string',
        'AGE_AT_ENTRY': pd.Int32Dtype(),
        'DURATIONIF_M': pd.Int32Dtype(),
        'EFF_YEAR': pd.Int32Dtype(),
        'EFF_MONTH': pd.Int32Dtype(),
        'EFF_DAY': pd.Int32Dtype(),
        'POL_TERM_Y': pd.Int32Dtype(),
        'PREM_FREQ': pd.Int32Dtype(),
        'PREM_PAYBL_M': pd.Int32Dtype(),
    },

    'MPF_INDEX_COLUMNS': [
        # Insert the column names you wish to be the index, e.g. POL_NUMBER, SPCODE
    ],
}
'''
