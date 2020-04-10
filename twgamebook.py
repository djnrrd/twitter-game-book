#!/usr/bin/env python
"""
Usage:
    twgamebook.py -s SOURCE -t CREDS [-d]

Options:
    -s SOURCE --source=SOURCE       Source file for the game, can be a local
                                    file or HTTP
    -t CREDS --twitter=CREDS        Path to twitter Oauth keys
    -d                              Switch debugging on in the log
"""
import logging
from docopt import docopt
from twgamebook import game

# Set my logging options
logger = logging.getLogger('twgamebook')
logger.setLevel(logging.INFO)
log_fh = logging.FileHandler('twgamebook.log')
log_fh.setLevel(logging.INFO)
log_format = logging.Formatter('%(asctime)s - %(levelname)s - %(''message)s',
                               datefmt='%b %d %H:%M')
log_fh.setFormatter(log_format)
logger.addHandler(log_fh)

def main(args):
    """Run the Twitter Game Book bot

    :param args: docopt created arguments from sysv
    :type args:dict"""
    if isinstance(args, dict):
        if args['-d']:
            logger.setLevel(logging.DEBUG)
            log_fh.setLevel(logging.DEBUG)
        logger.debug('Starting twgamebook')
        source_file = args['--source']
        my_game = game.twGameBook(source_file)
        print(my_game.read_section())
    else:
        raise KeyError('Expected Dictionary object as args')


if __name__ == '__main__':
    args = docopt(__doc__)

    main(args)
