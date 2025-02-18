# MPF Inspector

This is a python library to facilitate the processing of model points used for actuarial software [Prophet](https://www.prophet-web.com/prophet-products/prophet-professional/), produced by FIS (not the Prophet created by Facebook for time series forecast).

It utilizes the power of the [Pandas](https://pandas.pydata.org/) library so you can easily parse, process and filter the model points.

## System Requirement

Python >= 3.9

For Windows users new to Python, we recommend installing python wth Pandas using [Anaconda](https://www.anaconda.com/products/individual)
   - For users who are not familiar with Anaconda/python, please select "export to PATH" during the installation so your life can be easier for running with Python

## Installation

For normal machines without network restrictions:
```
pip install mpfi
```

If you encounter errors due to installing, you can either add `trusted-host` to the install command or use the wheel file:

```
pip install --trusted-host pypi.python.org --trusted-host files.pythonhosted.org --trusted-host pypi.org mpfi
 ```

### Wheel file approach:

1. Download the wheel file of mpfi from <https://pypi.org/project/mpfi/#files>

2. Install the wheel by running the following command:

```
pip install "C:/the-path-to-your-file.whl"
```

Reference: https://stackoverflow.com/questions/25981703/pip-install-fails-with-connection-error-ssl-certificate-verify-failed-certi

## Usage

### Quick Glance

```python
import pandas as pd
import mpfi
dtype = { 'SPCODE': pd.Int64Dtype() }
# read_csv_options is the options to be passed to pandas.read_csv
df = mpfi.load_mpf('example/C*.PRO', read_csv_options={ 'dtype': dtype })
# df['_PROD_NAME'] will store the PROD_NAME, e.g. `C123456`
# df['_EXTENSION'] will store the extension including the dot, e.g. `.PRO`
mpfi.export_mpf(df, 'output2/')

# Trailing slash or backslash is optional for folder name
# By default, only all columns with name starting with a Capital letter is outputted
mpfi.export(df, 'all-model-points/', {
    'include_columns': ['_FILE_NAME'],
    'exclude_columns': ['SPCODE', 'AGE_AT_ENTRY'],
    # the OUTPUT_FORMAT header line, default is mpfi
    'output_format': 'FORMAT_C',
})
```

### Loading .fac TABLE files

Sometimes you need to load some `.fac` file as used for DCS/Prophet for extra mapping.

This library provides a helper for loading the `fac` file, which automatically creates the corresponding index columns according to the `.fac` file.

```python
import mpfi
my_data = mpfi.load_fac('prem_rate.fac') # a pandas DataFrame object
# it also accepts read_csv_options for further customization
```

## Reference (example DataFrame operations)

```python
# select model points with policy number 12345678
df[df['POL_NUMBER'] == '12345678']

# inspect the model point
import pandas as pd
pd.options.display.max_rows = None # To set pandas to display all rows
df[df['POL_NUMBER'] == '12345678'].T # display it. (T means transpose)
pd.options.display.max_rows = 60 # restore display options

# select model points with policy number 12345678, with its SPCODE and SUM_ASSURED columns
df[df['POL_NUMBER'] == '12345678'][['SPCODE', 'SUM_ASSURED']]

# PREM_FREQ is 1 and plan code is either ABC or DEF
# The bracket is important here due to order of precedence for & or |
df[(df['PREM_FREQ'] == 1) & (df.PLAN_CODE.isin(['ABC', 'DEF']))]

# PREM_FREQ is 1 or EFF_YEAR is 2010
# The bracket is important here due to order of precedence for & or |
df[(df['PREM_FREQ'] == 1) | (df['EFF_YEAR'] == 2010)]

# Set PREM_FREQ to 12 for all model points
df['PREM_FREQ'] = 12

# Edit/Create exchange rate based on currency
df['exchange_rate'] = data['CURRENCY'].map({ 'HKD': 1/7.8, 'USD': 1, 'MOP': 1/7.8 })

# Filter by _PROD_CODE `C12345` or `C23456` and output the selection to csv for "easier" manipulation
df[df['_PROD_NAME'].isin(['C12345', 'C23456'])].to_csv('C12345-C23456.csv')
```

For more information on selecting and editing DataFrame, please visit the [documentation of Pandas](http://pandas.pydata.org/pandas-docs/stable/user_guide/).

## Motivation

In system design, the same type of data should be stored together, in one single file or one single database table. This can ensure consistency and facilitate indexing, searching and manipulation of data.

However, FIS Prophet structures itself in a way that "encourages" users to split the same type of data (policy data) across multiple files (different product codes), known as model point files "MPF". This creates problems for users to manage and manipulate hundreds of files, in different folders, since, in most insurance companies, a different model point file is used for every different product code, month and region, while the best practice is to store all these in one single database.

To add to the problem, while a normal csv file is easy to parse and analyze, Prophet made model point files harder to parse because of the extra header lines and footer lines produced by DCS, the data conversion system which aims to make producing model point files "easy". The same applies for the external tables used by Prophet and DCS, aka the .fac files.

With DCS's old-fashioned syntax, the codes are often unnecessary complicated; and with DCS configurations (e.g. input format) not stored as codes, proper version control and code collaboration are impossible, therefore we see `v1`, `v2`, `v202012` everywhere, and we frequently encounter the need for manual merging of DCS which is tedious and time-consuming.

To ease the maintenance difficulty posed by the above issues, I wrote this library to create more user-friendly methods to create, edit and filter model points.

Using Python with the Pandas library is one of the best ways to manage and create model point files, thanks to the modern Python features and syntax with great community support, and the ability to handle large amount of data with Pandas.

## License

This project is licensed under [MIT License](https://en.wikipedia.org/wiki/MIT_License).
