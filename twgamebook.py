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
import json
from datetime import datetime
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

def check_log():
    """Load the last position from the log, if present

    :return: Tuple of time, last stitch key and list of saved flags
    :rtype: tuple
    """
    with open('twgamebook.log', 'r') as log_file:
        logs = log_file.readlines()
    info_logs = [x for x in logs if 'INFO' in x]
    # If there's no log we start fresh
    if len(info_logs) > 0:
        # If the last info message was a game end, we start fresh
        if 'GAMEEND' in info_logs[-1]:
            return ()
        # Otherwise we pickup where we left off
        else:
            # Trim the newline character and split out the fields
            last_log = info_logs[-1]
            last_log = last_log.split(' - ')
            # Because the year is not in the log, this will come up as 1900
            last_time = datetime.strptime(last_log[0], '%b %d %H:%M')
            last_time = last_time.replace(datetime.now().year)
            last_key = last_log[2]
            last_flags = json.loads(last_log[3])
            return (last_time, last_key, last_flags)
    else:
        return ()


def main(args):
    """Run the Twitter Game Book bot

    :param args: docopt created arguments from sysv
    :type args:dict"""
    if isinstance(args, dict):
        if args['-d']:
            logger.setLevel(logging.DEBUG)
            log_fh.setLevel(logging.DEBUG)

        logger.debug('Starting twgamebook')
        last_pos = check_log()
        source_file = args['--source']
        my_game = game.twGameBook(source_file)
        #print(my_game.read_section())
    else:
        raise KeyError('Expected Dictionary object as args')


if __name__ == '__main__':
    args = docopt(__doc__)
    main(args)
