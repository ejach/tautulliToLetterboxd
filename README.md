# tautulliToLetterboxd
Export watched content from [Tautulli](https://github.com/tautulli/tautulli) to the [Letterboxd CSV Import Format](https://letterboxd.com/about/importing-data/).

## Installation
```bash
$ git clone https://github.com/ejach/tautulliToLetterboxd.git
$ cd tautulliToLetterboxd
$ pip install .
```
## Usage
1. Must have [Tautulli](https://github.com/tautulli/tautulli) installed
2. Edit the environment variables in `.env` to point to your Tautulli installation:
```bash
# The Tautulli host
# Default: http://localhost:8181
baseurl=http://localhost:8181
# Tautulli API token 
# Found in Settings > Web Interface > API Key
token=xxx
# Username (if set) or email
user=xxx
# File to output to in *.csv format
# Default: output.csv
filename=output.csv
```
3. Run using:
```bash
$ python src/main.py
```
## Author
[Evan J.](https://github.com/ejach)

Inspired by [mtimkovich/plex2letterboxd](https://github.com/mtimkovich/plex2letterboxd)
