import logging
import json
from textwrap import wrap
import re
from datetime import datetime, timedelta
from random import randint
from collections import Counter

# Get the log into this namespace
logger = logging.getLogger('twgamebook')


class TWGBGame(object):
    """An object for managing the game on Twitter

    :param story: TWGBStory object to play
    :type story: twgamebook.story.TWGBStory
    :param sleep_time: Time to sleep between threads
    :type sleep_time: str
    """
    def __init__(self, story, sleep_time):

        self.story = story
        if sleep_time[-1] == 'd':
            self.sleep_time = timedelta(days=int(sleep_time[:-1]))
        elif sleep_time[-1] == 'h':
            self.sleep_time = timedelta(hours=int(sleep_time[:-1]))
        elif sleep_time[-1] == 'm':
            self.sleep_time = timedelta(minutes=int(sleep_time[:-1]))
        else:
            raise ValueError("Sleep time expects 'd' 'h' or 'm'")


    def play(self):
        """Play the game
        """
        # We loop in here until the game ends
        game_end = False
        bookmark = ''
        while not game_end:
            # Check the log, set the tweet_id to 0 until it's overwritten
            last_pos = self._load_last_log()
            tweet_id = 0
            if last_pos:
                # Was it the end of the this game?
                if f"GAMEEND {self.story.title}" in last_pos:
                    logger.debug('Matching GAMEEND found in logs.')
                    game_end = True
                    continue
                else:
                    last_time = last_pos[0]
                    bookmark = last_pos[1]
                    self.story.set_flags(last_pos[2])
                    tweet_id = last_pos[3]
                    logger.debug(f"Got key {bookmark} and tweet {tweet_id} from "
                                 f"the log")
                    # Get the valid hashtags
                    valid_hashtags = self.story.get_hashtags(bookmark)
                    logger.debug(f"Valid hashtags should be {valid_hashtags}")
                    # Get the user hashtags. This is where the process will
                    # sleep
                    user_hashtags = self._gather_hashtags(tweet_id, last_time)
                    logger.debug(f"Got user hashtags {user_hashtags}")
                    bookmark = self._check_votes(user_hashtags, valid_hashtags)
            thread = self.story.get_section(bookmark)
            post = self._send_story(thread, tweet_id)
            logger.info(post)

    def _check_votes(self, user_hastags, valid_hashtags):
        """Check that user submitted hashtags are valid and return the key to
        the winning one

        :param user_hastags: The user submitted hashtags
        :type user_hastags: Counter
        :param valid_hashtags: The valid hashtags for this part of the story
        :type valid_hashtags: dict
        :return: The key for the next stitch in the story.
        :rtype: str
        """
        pass

    def _load_last_log(self):
        """Load the last game state from the log.

        If there is no log return an empty tuple, if the last message was a
        GAMEEND message return that.

        twgamebook.story object will log an INFO message with 'last_key' and
        'last_flags'
            Apr 23 21:47 - INFO - oppositeTheChamb - ["has_ring"]
        Which is immediately followed by an INFO message from the
        twgamebook.game object with the last_tweet sent
            Apr 23 21:47 - INFO - 669401

        :return: (last_time(datetime), last_key(str), last_flags(list),
            last_tweet(int)) or (game_end)
        :rtype: tuple
        """
        # Read the log file in, the extract all the 'INFO' messages from it
        with open('twgamebook.log', 'r') as log_file:
            logs = log_file.readlines()
        info_logs = [x for x in logs if 'INFO' in x]
        # If there's no log we start fresh because there should be at least 2
        # messages per twitter stitch.
        if len(info_logs) >= 2:
            # Trim the newline character and split out the fields
            # INFO messages should be in pairs of game info, tweet info
            last_game_log = info_logs[-2][:-1]
            last_game_log = last_game_log.split(' - ')
            last_tweet = info_logs[-1][:-1]
            last_tweet = last_tweet.split(' - ')[2]
            # Because the year is not in the log, this will come up as 1900
            last_time = datetime.strptime(last_game_log[0], '%b %d %H:%M')
            last_time = last_time.replace(datetime.now().year)
            last_game_key = last_game_log[2]
            if 'GAMEEND' in last_game_key:
                return (last_game_key)
            # Otherwise we pickup where we left off
            else:
                last_flags = json.loads(last_game_log[3])
                return (last_time, last_game_key, last_flags, last_tweet)
        else:
            return ()

    def _send_story(self, thread, tweet_id=0):
        """Send the next story stitch to output

        :param thread: The next story stitch to send
        :type thread: list
        :return: A random number to simulate twitter message ID
        :rtype: int
        """
        # Loop through the supplied stitches updating the latest tweet_id for
        # each post and return that back for the log
        for stitch in thread:
            tweet_id = self._send_stitch(stitch, tweet_id)
        return tweet_id

    def _send_stitch(self, stitch, tweet_id):
        pass

    def _gather_hashtags(self, tweet_id, last_time):
        """Sleep for the required time and then gather the hashtags from the
        replies

        :param tweet_id: Last tweet of the last stitch where we will be
            investigating replies
        :type tweet_id: int
        :param last_time: Datetime object of the time the last tweet
            was sent
        :type last_time: datetime
        :return: A list of hashtags submitted by users
        :rtype: list
        """
        pass

class TWGBConsoleGame(TWGBGame):
    """An object for managing the game on the console

    :param story: TWGBStory object to play
    :type story: twgamebook.story.TWGBStory
    :param sleep_time: Time to sleep between threads
    :type sleep_time: str
    """
    def _send_stitch(self, stitch, tweet_id):
        """Send the next story stitch to the console

        :param stitch: The next story stitch to send
        :type stitch: str
        :return: A random number to simulate twitter message ID
        :rtype: int
        """
        # First we need to check if we're over the 280 character limit which
        # the twitter api module obfuscates from us
        if len(stitch) > 280:
            # Make a list of the stitch broken at a word boundary around the 280
            # character point. Send that back up to send_story to manage the
            # recursion for us
            tweet_list = wrap(stitch, 280)
            new_id = self._send_story(tweet_list, tweet_id)
        else:
            # Print a new "tweet"
            new_id = randint(0, 1000000)
            print(f"==Replying to tweet_id - {tweet_id}==")
            print(stitch)
            print(f"=={new_id}==")
        return new_id

    def _gather_hashtags(self, tweet_id, last_time):
        """Instead of sleeping and then gathering the data from the twitter API
        we'll just gather them in the console.

        :param tweet_id: Last tweet of the last stitch where we will be
            investigating replies
        :type tweet_id: int
        :param last_time: Datetime object of the time the last tweet
            was sent
        :type last_time: datetime
        :return: The counts of hashtags submitted by users
        :rtype: Counter
        """
        # So instead of sleeping, we're going to collect input from the terminal
        # Work out how long we're 'sleeping' for and collect 'tweets' in a
        # bucket
        time_diff = datetime.now() - last_time
        user_hashtags = []
        while time_diff < self.sleep_time:
            # Ignore case by changing everything to upper case
            tweet = input('Enter a tweet: ').upper()
            pattern = re.compile('#[0-9A-Z]+')
            matches = pattern.findall(tweet)
            # I want a list of unique hashtags from this tweet no doublers
            matches = list(set(matches))
            user_hashtags += matches
            time_diff = datetime.now() - last_time
        # Add all the hashtags together
        all_hashtags = []
        for hashtag in user_hashtags:
            all_hashtags.append(hashtag)
        # Convert them to a Counter objects
        return Counter(all_hashtags)

    def _check_votes(self, user_hastags, valid_hashtags):
        """Check that user submitted hashtags are valid and return the key to
        the winning one

        :param user_hastags: The user submitted hashtags
        :type user_hastags: Counter
        :param valid_hashtags: The valid hashtags for this part of the story
        :type valid_hashtags: dict
        :return: The key for the next stitch in the story.
        :rtype: str
        """
        ret_str = ''
        print('====')
        for hashtag in user_hastags.most_common():
            if hashtag[0] in valid_hashtags and not ret_str:
                ret_str = valid_hashtags[hashtag[0]]
            if hashtag[0] in valid_hashtags:
                print(f"* {hashtag[0]} - {hashtag[1]} votes")
        return ret_str