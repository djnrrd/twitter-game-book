#!/usr/bin/env python
"""
Usage:
    twgamebook.py -s SOURCE [-n] [-d]

Options:
    -s SOURCE --source=SOURCE       Source file for the game, can be a local
                                    file or HTTP
    -n --no-twitter                 Use interactive console session for testing
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
        # Load the game
        source_file = args['--source']
        my_story = game.TWGBStory(source_file)
        if args['--no-twitter']:
            my_game = game.TWGBConsoleGame(my_story)
        else:
            my_game = game.TWGBGame(my_story)
        my_game.play()
    else:
        raise KeyError('Expected Dictionary object as args')


if __name__ == '__main__':
    args = docopt(__doc__)
    main(args)
