# tautulliToLetterboxd

[![PyPI](https://img.shields.io/pypi/v/requests?logo=python&label=requests&style=flat-square&color=FFD43B)](https://pypi.org/project/requests/)
[![PyPI](https://img.shields.io/pypi/v/pandas?logo=python&label=pandas&style=flat-square&color=FFD43B)](https://pypi.org/project/pandas/)
[![PyPI](https://img.shields.io/pypi/v/halo?logo=python&label=halo&style=flat-square&color=FFD43B)](https://pypi.org/project/halo/)
[![LGTM](https://img.shields.io/lgtm/grade/python/github/ejach/tautulliToLetterboxd?color=FFD43B&logo=python&style=flat-square)](https://lgtm.com/projects/g/ejach/tautulliToLetterboxd/)


Export watched content from [Tautulli](https://github.com/tautulli/tautulli) to the [Letterboxd CSV Import Format](https://letterboxd.com/about/importing-data/).

## Installation
```bash
$ git clone https://github.com/ejach/tautulliToLetterboxd.git
$ cd tautulliToLetterboxd
$ pip install -r requirements.txt
```
## Usage
1. Must have [Tautulli](https://github.com/tautulli/tautulli) (Atleast v2.1.34) installed
2. Edit the values in `config.ini` to point to your Tautulli installation:
```ini
[HOST]
# The Tautulli host
# Default: http://localhost:8181
baseurl=http://localhost:8181
[AUTH]
# Tautulli API token
# Found in Settings > Web Interface > API Key
token=xxx
```
3. Run using:
```bash
$ python -m tautulli_to_letterboxd [-h] [-i INI] [-o CSV] -u USER
```
```
# Export watched movie history from Tautulli in Letterboxd CSV format

optional arguments:
  -h, --help            show this help message and exit
  -i INI, --ini INI     config file to read from (default: cfg.ini)
  -o CSV, --csv CSV     *.csv file to output data to (default: output.csv)
  -u USER, --user USER  the username/email to get history from (default: None)

```
4. Upload the output file to https://letterboxd.com/import/
