import csv
import json
import os
from datetime import datetime

import pandas as pd
import requests as requests
from dotenv import load_dotenv

# Loads the .env file for the credentials
load_dotenv()

# Credentials specified in the .env file
baseurl = os.environ.get('baseurl')
token = os.environ.get('token')
user = os.environ.get('user')
filename = os.environ.get('filename')


# Handles the Tautulli API
def api_handler(base_url):
    headers = {'Content-Type': 'application/json'}
    response = requests.get(base_url, headers=headers)
    return json.loads(response.text)


# Handles the rating set by the user for any given movie
def rating_handler(rating):
    base_url = '{0}/api/v2?apikey={1}&cmd=get_metadata&rating_key={2}'.format(baseurl, token, rating)
    json_handler = api_handler(base_url)
    for _ in json_handler:
        root = json_handler['response']['data']
        # If root is empty, return empty string
        if root == {}:
            user_rating = ''
            return user_rating
        # Else, return user set rating
        else:
            user_rating = json_handler['response']['data']['user_rating']
            return user_rating


# Used to get the full length of a list to parse
def get_length():
    base_url = '{0}/api/v2?apikey={1}&cmd=get_history&media_type=movie&search={2}'.format(baseurl, token, user)
    json_data = api_handler(base_url)
    for _ in json_data:
        tot_count = json_data['response']['data']['recordsFiltered']
        return int(tot_count)


# Handles parsing the JSON from the API output
def json_parser():
    # Gets the total count of entries recorded and assigns it to an integer
    total_count = get_length()
    base_url = '{0}/api/v2?apikey={1}&cmd=get_history&media_type=movie&search={2}&length={3}'.format(baseurl, token,
                                                                                                     user, total_count)
    json_data = api_handler(base_url)
    movies = []
    print('Records to be filtered through: ' + str(total_count))
    for _ in json_data:
        # Value to be incremented through each loop pass
        count = 0
        # While the recordsFiltered doesn't equal our count value, continue
        while count <= total_count:
            # String either 1 or 0 that indicates if it has been watched before
            watched_status = json_data['response']['data']['data'][count]['watched_status']
            # Filters only content that has been watched
            if watched_status == 1:
                title = str(json_data['response']['data']['data'][count]['title'])
                year = str(json_data['response']['data']['data'][count]['year'])
                rating10 = rating_handler(str(json_data['response']['data']['data'][count]['rating_key']))
                date = int(json_data['response']['data']['data'][count]['date'])
                watched_date = datetime.fromtimestamp(date).strftime("%Y-%m-%d")
                movies.append(title + ',' + year + ',' + rating10 + ',' + watched_date)
                print(str(len(movies)) + '->' + title)
            count += 1
            if count == total_count:
                return movies, count


# Handles outputting the JSON values into the Letterboxd CSV format
def to_csv():
    movies, count = json_parser()
    data_file = open('output.csv', 'w')
    # Header that is specified by Letterboxd
    header = ['Title,Year,Rating10,WatchedDate']
    # Create the CSV writer object
    csv_writer = csv.writer(data_file, quoting=csv.QUOTE_NONE, quotechar=None, delimiter='\n')
    csv_writer.writerow(header)
    csv_writer.writerow(movies)
    data_file.close()
    print(f'Exported filtered movies to {filename}.')
    # After writing to the file, check for duplicate entries
    check_duplicates()


# Checks if there are duplicates in the CSV output
def check_duplicates():
    data = pd.read_csv('output.csv', index_col=0)
    # Drop the duplicates:
    clean_data = data.drop_duplicates(keep='last')
    # Save the filtered data:
    clean_data.to_csv("output.csv")
    print('Duplicate entries (if any) have been dropped')


if __name__ == '__main__':
    to_csv()
