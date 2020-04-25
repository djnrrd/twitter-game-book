"""
Usage:
    runtwgb -s SOURCE -t PERIOD [-n] [-d]

Options:
-s SOURCE --source=SOURCE       Source file for the game, can be a local
                                file or HTTP
-t PERIOD --sleep-time=PERIOD   Period to sleep between threads in the game
                                for example 24h, 3d, 1h

-n --no-twitter                 Use interactive console session for testing
-d                              Switch debugging on in the log
"""
import logging
from docopt import docopt
from . import game, story

# Set my logging options
logger = logging.getLogger('twgamebook')
logger.setLevel(logging.INFO)
log_fh = logging.FileHandler('twgamebook.log')
log_fh.setLevel(logging.INFO)
log_format = logging.Formatter('%(asctime)s - %(levelname)s - %(''message)s',
                               datefmt='%b %d %H:%M')
log_fh.setFormatter(log_format)
logger.addHandler(log_fh)

def main():
    args = docopt(__doc__)
    if args['-d']:
        logger.setLevel(logging.DEBUG)
        log_fh.setLevel(logging.DEBUG)
    logger.debug('Starting twgamebook')
    # Load the game
    source_file = args['--source']
    sleep_time = args['--sleep-time']
    my_story = story.TWGBStory(source_file)
    if args['--no-twitter']:
        my_game = game.TWGBConsoleGame(my_story, sleep_time)
    else:
        my_game = game.TWGBGame(my_story, sleep_time)
    my_game.play()


if __name__ == '__main__':
    main()