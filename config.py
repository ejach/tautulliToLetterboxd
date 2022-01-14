from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
from configparser import ConfigParser


def arg_parse():
    # Parse arguments from CLI arguments
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


class App:
    # Construct the argument parser
    ARGS = arg_parse()

    # Construct the config parser
    CFG = ConfigParser()
    CFG.read(ARGS.ini)

    # Credentials specified in the *.ini file and the CLI arguments
    __conf = {
        'base_url': CFG['HOST']['base_url'],
        'token': CFG['AUTH']['token'],
        'user': ARGS.user,
        'file_name': ARGS.csv
    }

    # Return the credential value by the key name
    @staticmethod
    def config(name):
        return App.__conf[name]
