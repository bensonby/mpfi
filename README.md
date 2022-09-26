# MPF Inspector

This is a python library to facilitate the processing of model points used for actuarial software [Prophet](https://www.prophet-web.com/prophet-products/prophet-professional/), produced by FIS (not the Prophet created by Facebook for time series forecast).

It utilizes the power of the [Pandas](https://pandas.pydata.org/) library so you can easily parse, process and filter the model points.

## System Requirement

Python >= 3.6

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
# in a python command shell, or as Python script
import mpfi

# mpfi.load or mpfi.load_all returns a pandas DataFrame object

# load the first model point with file name C123456 in the list of paths provided in the config
df = mpfi.load('C123456')

# load all C product model points in the first folder found with 201912
df = mpfi.load_all('201912', 'C*.PRO')

# output the data as model point files in folder `all-model-points`
mpfi.export(df, 'all-model-points')

# output (consolidate) all model points in single file `all-model-points.PRO` without the header
# header means the 3 extra header lines in the MPF: OUTPUT_FORMAT, NUMLINES and VARIABLE_TYPES
mpfi.export(df, 'all-model-points', { 'split_into_prod': False, 'write_header': False })

# same as above but also include the _FILE_NAME and exclude the SPCODE and AGE_AT_ENTRY columns
# header means the 3 extra header lines in the MPF: OUTPUT_FORMAT, NUMLINES and VARIABLE_TYPES
mpfi.export(df, 'all-model-points', {
    'split_into_prod': False,
    'write_header': False,
    'include_columns': ['_FILE_NAME'],
    'exclude_columns': ['SPCODE', 'AGE_AT_ENTRY'],
})
```

### Reference (example DataFrame operations)

```python
# select model points with policy number 12345678
df[df.POL_NUMBER == '12345678']

# inspect the model point
import pandas as pd
pd.options.display.max_rows = None # To set pandas to display all rows
df[df.POL_NUMBER == '12345678'].T # display it. (T means transpose)
pd.options.display.max_rows = 60 # restore display options

# select model points with policy number 12345678, with its SPCODE and SUM_ASSURED columns
df[df.POL_NUMBER == '12345678'][['SPCODE', 'SUM_ASSURED']]

# PREM_FREQ is 1 and plan code is either ABC or DEF
df[(df.PREM_FREQ == 1) & (df.PLAN_CODE.isin(['ABC', 'DEF']))]

# PREM_FREQ is 1 or EFF_YEAR is 2010
df[(df.PREM_FREQ == 1) | (df.EFF_YEAR == 2010)]

# Set PREM_FREQ to 12 for all model points
df['PREM_FREQ'] = 12

# Edit/Create exchange rate based on currency
df['exchange_rate'] = data['CURRENCY'].map({ 'HKD': 1/7.8, 'USD': 1, 'MOP': 1/7.8 })

# Filter by _PROD_CODE `C12345` or `C23456` and output the selection to csv for "easier" manipulation
df[(df._PROD_NAME == 'C12345') | (df._PROD_NAME == 'C23456')].to_csv('C12345-C23456.csv')
```

For more information on selecting and editing DataFrame, please visit the [documentation of Pandas](http://pandas.pydata.org/pandas-docs/stable/user_guide/).

### Configuration file

Before using the library, you should create and configure the specification file `mpfi-config.py` for your company and work environment.

The library will automatically load the config file `mpfi-config.py` in the current path when any `load` function is executed.

You can run `mpfi.generate_config()` to create a sample config file so you can further modify it. The config file includes explanation so it should be self-explantory.

```python
import mpfi
mpfi.generate_config() # Create mpfi-config.py in the current folder for editing
```

To utilize the library, you are advised to put in the MPF path of every month/region as applicable. You will be able to select the right MPF by giving constraints.

### Loading a single model point file

The product code itself will be inserted to the DataFrame with column name specified in the config (default is `_PROD_NAME`).

Similarly the full file path is inserted as `_FILE_NAME`.

```python
import mpfi

# Assuming config extension is .PRO

# load the first C123456.PRO found in the list of MPF_FOLDERS
df = mpfi.load('C123456') # a pandas DataFrame object

# load the first C123456.PRO found in the list of MPF_FOLDERS where the full file path contains 201912
df = mpfi.load('C123456', '201912') # a pandas DataFrame object

# load the first C123456.PRO found in the list of MPF_FOLDERS
# where the full file path contains both 201912 and HK
df = mpfi.load('C123456', ['HK', '201912']) # a pandas DataFrame object
```

### Loading multiple model point files in a folder

```python
mpfi.load_all(containing_text, file_pattern=None)
```

The product code itself will be inserted to the DataFrame with column name specified in the config (default is `_PROD_NAME`)

#### Examples

```python
import mpfi

# Assuming config extension is .PRO

# load all *.PRO in the first MPF folder containing 201912
df = mpfi.load_all('201912')

# load all C*.rpt in the first MPF folder containing both HK and 201912
# Note that the config extension is ignored when a specific file pattern is provided
df = mpfi.load_all(['201912', 'HK'], 'C*.rpt')
```

### Loading .fac TABLE files

Sometimes you need to load some `.fac` file as used for DCS/Prophet for extra mapping.

This library provides a helper for loading the `fac` file, which automatically creates the corresponding index columns according to the `.fac` file.

```python
import mpfi
my_data = mpfi.load_fac('prem_rate.fac') # a pandas DataFrame object
```

The file extension for the fac file is defined in the config as `FAC_EXTENSION` (default `fac`), and the folders to be searched for are defined in `FAC_FOLDERS` (default `['./', 'TABLES/', 'example/']`)


### Customization upon reading and saving as CSV

You can supply optional argument to the underlying `pandas.read_csv` function in the `load`, `load_all` or `load_fac` function by passing a dictionary to the optional argument `read_csv_options`, e.g.

```python
import mpfi
my_data = mpfi.load('C123456', read_csv_options={'usecols': ['ANNUAL_PREM', 'AGE_AT_ENTRY']})
```

The same also applies for `to_csv_options` in `mpfi.export`:

```python
import mpfi
my_data = mpfi.load('C123456')
mpfi.export(my_data, to_csv_options={'sep': '|'})
```

## Motivation

In system design, the same type of data should be stored together, in one single file or one single database table. This can ensure consistency and facilitate indexing, searching and manipulation of data.

However, FIS Prophet structures itself in a way that "encourages" users to split the same type of data (policy data) across multiple files (different product codes), known as model point files "MPF". This creates problems for users to manage and manipulate hundreds of files, in different folders, since, in most insurance companies, a different model point file is used for every different product code, month and region, while the best practice is to store all these in one single database.

To add to the problem, while a normal csv file is easy to parse and analyze, Prophet made model point files harder to parse because of the extra header lines and footer lines produced by DCS, the data conversion system which aims to make producing model point files "easy". The same applies for the external tables used by Prophet and DCS, aka the .fac files.

With DCS's old-fashioned syntax, the codes are often unnecessary complicated; and with DCS configurations (e.g. input format) not stored as codes, proper version control and code collaboration are impossible, therefore we see `v1`, `v2`, `v202012` everywhere, and we frequently encounter the need for manual merging of DCS which is tedious and time-consuming.

To ease the maintenance difficulty posed by the above issues, I wrote this library to create more user-friendly methods to create, edit and filter model points.

Using Python with the Pandas library is one of the best ways to manage and create model point files, thanks to the modern Python features and syntax with great community support, and the ability to handle large amount of data with Pandas.

## License

This project is licensed under [MIT License](https://en.wikipedia.org/wiki/MIT_License).
