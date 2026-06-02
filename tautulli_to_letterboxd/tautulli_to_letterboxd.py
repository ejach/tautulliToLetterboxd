from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
from configparser import ConfigParser
from csv import QUOTE_ALL, writer
from datetime import datetime
from json import loads, JSONDecodeError
from sys import exit
from typing import Optional, Tuple
from urllib.error import URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from tautulli_to_letterboxd.spinner import Loading


# Parse arguments from CLI arguments
def arg_parse() -> iter:
    parser = ArgumentParser(
        description='Export watched movie history from Tautulli in Letterboxd CSV format',
        formatter_class=ArgumentDefaultsHelpFormatter)
    # The *.ini file to read from
    parser.add_argument('-i', '--ini', default='config.ini',
                        help='config file to read from')
    # The *.csv file to output data to
    parser.add_argument('-o', '--csv', default='output.csv',
                        help='*.csv file to output data to')
    # The username/email to get history from
    parser.add_argument('-u', '--user', required=True,
                        help='the username/email to get history from')
    return parser.parse_args()


# Construct the argument parser
ARGS = arg_parse()

# Construct the config parser
CFG = ConfigParser()
CFG.read(ARGS.ini)

# Credentials specified in the *.ini file and the CLI arguments
BASE_URL = f"{CFG['HOST']['base_url']}/api/v2"
TOKEN = CFG['AUTH']['token']
USER = ARGS.user
FILE_NAME = ARGS.csv

# Loading animation
LOADING = Loading()


# Handles the Tautulli API
def api_handler(params: dict) -> dict:
    try:
        params['apikey'] = TOKEN
        query = urlencode(params)
        url = f"{BASE_URL}?{query}"
        req = Request(
            url,
            headers={'Content-Type': 'application/json'},
            method='GET'
        )
        with urlopen(req) as response:
            return loads(response.read().decode('utf-8'))

    except URLError as e:
        LOADING.fail('Base URL invalid, please try again\n' + str(e))
        exit(1)


# Handles the rating set by the user for any given movie
def rating_handler(rating_key: str) -> Optional[Tuple[str, str, str]]:
    user_rating = ''
    tmdb_id = ''
    imdb_id = ''
    json_data = api_handler(params={'cmd': 'get_metadata', 'rating_key': rating_key})
    for _ in json_data:
        # If root is empty, return
        if json_data['response']['data']:
            user_rating = json_data['response']['data']['user_rating']
            for guid in json_data['response']['data']['guids']:
                if guid.startswith('tmdb'):
                    tmdb_id = guid.split('://')[1]
                if guid.startswith('imdb'):
                    imdb_id = guid.split('://')[1]
    return user_rating, tmdb_id, imdb_id


# Handles parsing the JSON from the API output
def json_parser() -> tuple:
    try:
        movies = []
        # Gets the total count of entries recorded and assigns it to an integer
        total_count = api_handler(params={'cmd': 'get_history', 'media_type': 'movie',
                                          'search': USER})['response']['data']['recordsFiltered']
        # Sends the params to the api_handler
        json_data = api_handler(params={'cmd': 'get_history', 'media_type': 'movie', 'search': USER,
                                        'length': total_count})
        # Make sure the user exists and that they have sufficient watch history
        if total_count > 0:
            print(f'Exporting movies to {FILE_NAME} for user {USER}:')
            for count, _ in enumerate(json_data['response']['data']['data']):
                # String either 1 or 0 that indicates if it has been watched before
                watched_status = json_data['response']['data']['data'][count]['watched_status']
                # Filters only content that has been watched
                if watched_status == 1:
                    # Gets the movie title
                    title = str(json_data['response']['data']['data'][count]['title'])
                    # Gets the release year
                    year = str(json_data['response']['data']['data'][count]['year'])
                    # Gets the user_rating from the rating_handler and returns a value if it exists
                    rating10, tmdb_id, imdb_id = rating_handler(str(json_data['response']['data']['data'][count]['rating_key']))
                    # Gets the date watched then puts it in YYYY-MM-DD format
                    watched_date = datetime.fromtimestamp(int(json_data['response']['data']['data'][count]['date'])
                                                          ).strftime('%Y-%m-%d')
                    row = [title, year, rating10, tmdb_id, imdb_id, watched_date]
                    # Append the movie entries to the list and drop the duplicates if any exist
                    movies.append(row) if row not in movies else None
                    # Start the loading animation
                    LOADING.start(text=f'{str(len(movies))} -> {title}')
            return movies, len(movies)
        # Otherwise, exit
        else:
            LOADING.fail('Username is invalid or the specified user has insufficient watch history. '
                         'Please check your configuration and try again'), exit()
    except IndexError as e:
        LOADING.fail('Index Error, please check your configuration and try again' + '\n' + str(e))
    except KeyError as e:
        LOADING.fail('API key invalid, please try again' + '\n' + str(e))



# Write the collected data to the specified CSV file
def to_csv() -> None:
    try:
        movies, movies_length = json_parser()
        with open(FILE_NAME, 'w', encoding='utf-8', newline='') as data_file:
            csv_writer = writer(data_file, quoting=QUOTE_ALL, quotechar='"')
            csv_writer.writerow(['Title', 'Year', 'Rating10', 'tmdbID', 'imdbID', 'WatchedDate'])
            for movie in movies:
                csv_writer.writerow(movie)
        LOADING.succeed(f'Exported {movies_length} filtered movies to {FILE_NAME} from user {USER}.')
    except KeyboardInterrupt:
        LOADING.fail(f'Exporting movies to {FILE_NAME} has been halted.')
    except JSONDecodeError as e:
        LOADING.fail(f'Loading failed. Please check your configuration and try again.\n{str(e)}')

def main() -> None:
    to_csv()