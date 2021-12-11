from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
from configparser import ConfigParser
from csv import QUOTE_NONE, writer
from datetime import datetime
from json import loads

from halo import Halo
from pandas import read_csv
from requests import get, exceptions


# Parse arguments from CLI arguments
def arg_parse():
    parser = ArgumentParser(
        description='Export watched movie history from Tautulli in Letterboxd CSV format',
        formatter_class=ArgumentDefaultsHelpFormatter)
    # The *.ini file to read from
    parser.add_argument('-i', '--ini', default='config.ini',
                        help='config file to read from')
    # The *.csv file to output data to
    parser.add_argument('-o', '--csv', default='output.csv',
                        help='*.csv file to output data to')
    return parser.parse_args()


# Construct the argument parser
args = arg_parse()

# Construct the config parser
cfg = ConfigParser()
cfg.read(args.ini)

# Credentials specified in the *.ini file and the CLI arguments
baseurl = cfg['HOST']['baseurl']
token = cfg['AUTH']['token']
user = cfg['AUTH']['user']
filename = args.csv


# Handles the Tautulli API
def api_handler(base_url):
    try:
        headers = {'Content-Type': 'application/json'}
        response = get(base_url, headers=headers)
        return loads(response.text)
    except exceptions.ConnectionError as e:
        print(str(e) + '\n' + 'API key or Base URL invalid, please try again')


# Handles the rating set by the user for any given movie
def rating_handler(rating):
    base_url = f'{baseurl}/api/v2?apikey={token}&cmd=get_metadata&rating_key={rating}'
    json_handler = api_handler(base_url)
    for _ in json_handler:
        root = json_handler['response']['data']
        # If root is empty, return empty string
        if not root:
            return ''
        # Else, return user set rating
        else:
            user_rating = json_handler['response']['data']['user_rating']
            return user_rating


# Used to get the full length of a list to parse
def get_length():
    base_url = f'{baseurl}/api/v2?apikey={token}&cmd=get_history&media_type=movie&search={user}'
    json_data = api_handler(base_url)
    for _ in json_data:
        tot_count = int(json_data['response']['data']['recordsFiltered'])
        return tot_count


# Handles parsing the JSON from the API output
def json_parser():
    # Gets the total count of entries recorded and assigns it to an integer
    total_count = get_length()
    # URL to obtain the records from with the total_count passed
    base_url = f'{baseurl}/api/v2?apikey={token}&cmd=get_history&media_type=movie&search={user}&length={total_count}'
    # Sends the final URL to the api_handler
    json_data = api_handler(base_url)
    # Loading animation
    loading = Halo(spinner='bouncingBar')
    movies = []
    print(f'Exporting movies to {filename} for user {user}: ')
    try:
        for _ in json_data:
            # Value to be incremented through each loop pass
            count = 0
            # While the recordsFiltered doesn't equal our count value, continue
            while count <= total_count:
                # String either 1 or 0 that indicates if it has been watched before
                watched_status = json_data['response']['data']['data'][count]['watched_status']
                # Filters only content that has been watched
                if watched_status == 1:
                    # Gets the movie name
                    name = str(json_data['response']['data']['data'][count]['title'])
                    # Checks if the movie has a comma (,) in it, encapsulates title in quotes "" if true, returns title
                    # if false
                    title = '"%s"' % ' '.join([a.strip() for a in name.split('\n') if a]) if ',' in name else name
                    # Gets the release year
                    year = str(json_data['response']['data']['data'][count]['year'])
                    # Gets the user_rating from the rating_handler and returns a value if it exists
                    rating10 = rating_handler(str(json_data['response']['data']['data'][count]['rating_key']))
                    # Gets the date watched then puts it in YYYY-MM-DD format
                    watched_date = datetime.fromtimestamp(int(json_data['response']['data']['data'][count]['date'])). \
                        strftime('%Y-%m-%d')
                    movies.append(f'{title},{year},{rating10},{watched_date}')
                    # Start the loading animation
                    loading.start(text=f'{str(len(movies))} -> {title}')
                count += 1
                # When the count variable equals the total recordsFiltered, stop and return the movies list
                if count == total_count:
                    # Stop the loading animation
                    loading.stop()
                    return movies, len(movies)
    except IndexError as e:
        print(str(e) + '\n' + 'Invalid user, please check your configuration and try again')


# Handles outputting the JSON values into the Letterboxd CSV format
def to_csv():
    # Get the movies list and its length
    movies, movies_length = json_parser()
    with open(filename, 'w') as data_file:
        # Header that is specified by Letterboxd
        header = ['Title,Year,Rating10,WatchedDate']
        # Create the CSV writer object
        csv_writer = writer(data_file, quoting=QUOTE_NONE, quotechar=None, delimiter='\n')
        # Write the header
        csv_writer.writerow(header)
        # Write the list
        csv_writer.writerow(movies)
    print(f'Exported {movies_length} filtered movies to {filename}.')
    # After writing to the file, check for duplicate entries
    check_duplicates()


# Checks if there are duplicates in the CSV output
def check_duplicates():
    data = read_csv(filename, index_col=0)
    # Drop the duplicates, keep the last recorded duplicate
    clean_data = data.drop_duplicates(keep='last')
    # Save the filtered data
    clean_data.to_csv(filename)
    total_count = get_length() - clean_data.shape[0] if clean_data.shape[0] else None
    print(f'{total_count} duplicate entries have been dropped' if total_count else 'No duplicate entries have been '
                                                                                   'dropped')
