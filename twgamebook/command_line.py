"""
Usage:
    runtwgb -s SOURCE -t PERIOD [-n] [-d] [-f OPTION]

Options:
-s SOURCE --source=SOURCE       Source file for the game, can be a local
                                file or HTTP
-t PERIOD --sleep-time=PERIOD   Period to sleep between threads in the game
                                for example 24h, 3d, 1h

-n --no-twitter                 Use interactive console session for testing
-d                              Switch debugging on in the log
-f --force-option=OPTION        Force a particular hashtag to be used on the
                                next decision
"""
import logging
from docopt import docopt
from twgamebook import game, story

# Set my logging options
LOGGER = logging.getLogger('twgamebook')
LOGGER.setLevel(logging.INFO)
_LOG_FH = logging.FileHandler('twgamebook.log')
_LOG_FH.setLevel(logging.INFO)
_log_format = logging.Formatter('%(asctime)s - %(levelname)s - %(''message)s',
                                datefmt='%b %d %H:%M')
_LOG_FH.setFormatter(_log_format)
LOGGER.addHandler(_LOG_FH)

def main():
    args = docopt(__doc__)
    if args['-d']:
        LOGGER.setLevel(logging.DEBUG)
        _LOG_FH.setLevel(logging.DEBUG)
    LOGGER.debug('Starting twgamebook')
    # Load the game
    source_file = args['--source']
    sleep_time = args['--sleep-time']
    my_story = story.TWGBStory(source_file)
    if args['--no-twitter']:
        my_game = game.TWGBConsoleGame(my_story, sleep_time)
    else:
        my_game = game.TWGBGame(my_story, sleep_time)
    if args['--force-option']:
        force_htag = args['--force-option']
    else:
        force_htag = ''
    my_game.play(force_htag=force_htag)


if __name__ == '__main__':
    main()
