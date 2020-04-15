import logging
import json
from textwrap import wrap
import re
import requests
from datetime import datetime, timedelta
from random import randint
from collections import Counter

# Get the log into this namespace
logger = logging.getLogger('twgamebook')


class TWGBStitch(object):
    """An object for managing the individual stitches of the story
    """

    def __init__(self, key, stitch):
        """Generate a twgbSwitch object from the source JSON

        :param key: The stitch key from the source JSON
        :type key: str
        :param stitch: The stitch data
        :type stitch: dict
        """
        logger.debug(f"Building switch obect {key}")
        self.key = key
        self.content = stitch['content'][0]
        self.divert = ''
        self.options = []
        self.flag_names = []
        self.if_conditions = []
        self.not_if_conditions = []
        self.page_num = 0
        self.page_label = ''
        options_list = [x for x in stitch['content'] if isinstance(x, dict)]
        for option in options_list:
            if 'divert' in option:
                logger.debug(f"Adding divert to {option['divert']}")
                self.divert = option['divert']
            if 'option' in option:
                logger.debug(f"Adding options {option}")
                self.options.append(option)
            if 'flagName' in option:
                logger.debug(f"Adding flag {option['flagName']}")
                self.flag_names.append(option['flagName'])
            if 'pageNum' in option:
                logger.debug(f"Adding page_num {option['pageNum']}")
                self.page_num = option['pageNum']
            if 'pageLabel' in option:
                logger.debug(f"Adding page_label {option['pageLabel']}")
                self.page_label = option['pageLabel']
            if 'ifCondition' in option:
                logger.debug(f"Adding if_condition {option['ifCondition']}")
                self.if_conditions.append(option['ifCondition'])
            if 'notIfCondition' in option:
                logger.debug(f"Adding not_if_condition"
                             f" {option['notIfCondition']}")
                self.not_if_conditions.append(option['notIfCondition'])

    def __repr__(self):
        return self.key

    def __str__(self):
        return self.key


class TWGBStory(object):
    """An object for loading JSON files from inklewriter.com
    """

    def __init__(self, source):
        """Build the twgamebook object

        :param source_file: The file path or URL to the source text
        :type source_file: str"""
        if isinstance(source, str):
            if source[0:8] == 'https://':
                source_data = self._load_http_json(source)
            else:
                source_data = self._load_local_json(source)
            if 'title' and 'data' in source_data:
                self.title = source_data['title']
                self.author = source_data['data']['editorData']['authorName']
                self.initial = source_data['data']['initial']
                self.stitches = self._load_stitches(source_data['data'][
                                                         'stitches'])
                self.flags = []
            else:
                logger.warning('Did not find expected Inklewriter JSON object')
                raise ValueError('Expected Inklewriter JSON object')
        else:
            raise KeyError('Expected string object as source')

    def _load_http_json(self, source_url):
        """Get the source file from the internet

        :param source_url:
        :type source_url: str
        :return: Parsed JSON object
        """
        logger.debug(f"{source_url} provided as URL")
        # Get the file via requests. If it raises as error, so be it
        r = requests.get(source_url)
        # We should get a 200, otherwise we'll raise an error through the
        # Response
        if r.status_code == 200:
            source_json = r.json()
            return source_json
        else:
            r.raise_for_status()

    def _load_local_json(self, source_file):
        """Get the source file from local disk

        :param source_file: Path to the locally stored source file
        :type source_file: str
        :return: The parsed JSON object
        """
        try:
            logger.debug(f"Attempting to open {source_file}")
            with open(source_file, 'r') as f:
                source_json = json.loads(f.read())
        except FileNotFoundError:
            logger.warning(f"Could not open {source_file}")
            raise ValueError(
                f"Source file {source_file} must either be a local "
                f"file or HTTP file")
        except json.JSONDecodeError:
            logger.warning(f"Could not parse JSON from {source_file}")
            raise json.JSONDecodeError()
        return source_json

    def _load_stitches(self, stitches):
        """Generate a list of TWGBStitch objects

        :param stitches: Dictionary of stitches from the JSON source file
        :type stitches: dict
        :return: List of twgbSwitch objects
        :rtype: list
        """
        ret_list = []
        for key in stitches:
            ret_list.append(TWGBStitch(key, stitches[key]))
        return ret_list

    def _get_stitch(self, key):
        """Return an individual stitch by it's key
        :param key: The key for the stitch to return
        :type key: str
        :return: The individual stitch
        :rtype: TWGBStitch
        """
        stitch = [x for x in self.stitches if x.key == key]
        if stitch:
            return stitch.pop()
        else:
            return None

    def _get_options(self, options):
        """Generate the thread endings when options are present on the stitch

        :param options: The list of options from the stitch
        :type options: list
        :return: List of thread ending tweets
        :rtype: list
        """
        # First thing is to filter the options down if there are conditions
        # attached to them
        filtered_options = []
        for option in options:
            if option['ifConditions']:
                if_conditions = [x['ifCondition'] for x in
                                 option['ifConditions']]
            else:
                if_conditions = []
            if option['notIfConditions']:
                not_if_conditions = [x['notIfCondition'] for x in option[
                    'notIfConditions']]
            else:
                not_if_conditions = []
            if self._pass_conditions(if_conditions, not_if_conditions):
                filtered_options.append(option)
        # Filtering done are we left with only one option? If we're left with
        # none we've broken the game and it's likely broken on inklewriter as
        # well
        if len(filtered_options) == 1:
            pass
            next_key = filtered_options[0]['linkPath']
            return self._get_stitch(next_key)
        else:
            # Let's go!
            ret_str = 'Should we:\n\n'
            for option in filtered_options:
                ret_str += f"* {option['option']}\n"
            ret_str += '\n\nReply to this tweet with your preferred Hashtag'
            return ret_str

    def _pass_conditions(self, if_conditions=[], not_if_conditions=[]):
        """ Check the conditions related to displaying the option or stitch

        :param if_conditions: List of the ifConditions flags to check for
        :type if_conditions: list
        :param not_if_conditions: List of the notIfConditions flags to check for
        :type not_if_conditions: list
        :return: True or False
        :rtype: bool
        """
        # Assume things are true
        if_result = True
        not_if_result = True
        if if_conditions:
            if_result = all(item in self.flags for item in if_conditions)
        if not_if_conditions:
            not_if_result = any(item not in self.flags for item in
                                not_if_conditions)
        return if_result and not_if_result

    def get_section(self, start_key='', _ret_str=''):
        """Read a section of the game until options or an ending is found

        :param start_key: The key for the starting stitch of the story. Leaving
            this blank will start the story from the beginning
        :type start_key: str
        :param _ret_str: The cumulative previously returned thread, used in
            recursion
        :type _ret_str: str
        :return: A list of tweets made up of all the stitches for this section.
        :rtype: list
        """
        # _ret_str isn't being cleared when the method finishes, leading to
        # subsequent calls being a cumulative version of the results. Must be a
        # pythonic quirk I need to learn more about.
        if not _ret_str or not isinstance(_ret_str, str):
            _ret_str = ''
        if not start_key or not isinstance(start_key, str):
            start_key = self.initial
        logger.debug(f"using Stitch ID {start_key}")
        stitch = self._get_stitch(start_key)
        if stitch:
            # Update game flags
            self.flags += stitch.flag_names
            # Check if we display this stitch:
            if self._pass_conditions(stitch.if_conditions,
                                     stitch.not_if_conditions):
                _ret_str += stitch.content
            # Now look if we need to keep going to the next piece
            if stitch.divert:
                # Break the paragraph up
                _ret_str += '\n\n'
                return self.get_section(stitch.divert, _ret_str)
            # Or generate our options, there shouldn't be both
            elif stitch.options:
                # Write the option key and flags to the log
                logger.info(f"{stitch.key} - {json.dumps(self.flags)}")
                # Format the options, if there aren't any the next stitch
                # will be returned instead
                option_tweets = self._get_options(stitch.options)
                if isinstance(option_tweets, TWGBStitch):
                    return self.get_section(option_tweets.key, _ret_str)
                else:
                    _ret_str += option_tweets
                    return _ret_str
            # Otherwise we've reached an ending
            else:
                # Write that we ended to the log
                logger.info(f"GAMEEND {self.title}")
                _ret_str += f"\n\nThank you for playing {self.title} by" \
                            f" {self.author}"
                return _ret_str
        else:
            logger.warning(f"Could not find {start_key} in the game")
            raise KeyError(f"Could not find {start_key} in the game")

    def get_hashtags(self, key):
        """Get the hashtags associated with the options

        :param key: The key of the stitch containing the options
        :type key: str
        :return: A List of hashtags and associated stitch keys
        :rtype: list
        """
        if isinstance(key, str):
            logger.debug(f"Looking for hashtags in {key}")
            stitch = self._get_stitch(key)
            if stitch:
                ret_dict = {}
                pattern = re.compile('#[0-9a-zA-Z]+')
                for option in stitch.options:
                    hash_tags = pattern.findall(option['option'])
                    stitch_key = option['linkPath']
                    if len(hash_tags) == 1:
                        ret_dict[hash_tags[0].upper()] = stitch_key
                    else:
                        logger.warning(f"Expected to find 1 hashtag in "
                                       f"{option['option']}")
                        raise ValueError('Expected to find 1 hashtag')
                return ret_dict
            else:
                logger.warning(f"Could not find {key} in the game")
                raise KeyError(f"Could not find {key} in the game")
        else:
            raise KeyError('string expected as key')

    def set_flags(self, flags):
        """Set the flags for the story externally

        :param flags: A list of flags to set in the story
        :type flags: list
        :return: True when set.
        :rtype: bool
        """
        if isinstance(flags, list):
            self.flags = flags
            return True
        else:
            raise KeyError('list expected as flags')


class TWGBGame(object):

    def __init__(self, story, sleep_time):
        """An object for managing the game

        :param story: TWGBStory object to play
        :type story: TWGBStory
        :param sleep_time: Time to sleep between threads
        :type sleep_time: str
        """
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
            # Check the log,
            last_pos = self._load_last_log()
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
            post = self._send_story(thread)
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

        :return: (last_time, last_key, last_flags, last_tweet) or (game_end)
        :rtype: tuple
        """
        with open('twgamebook.log', 'r') as log_file:
            logs = log_file.readlines()
        info_logs = [x for x in logs if 'INFO' in x]
        # If there's no log we start fresh because there should be at least 2
        # messages per twitter thread.
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

    def _send_story(self, thread):
        """Send the next story thread to twitter

        :param thread: The next story thread to send
        :type thread: str
        """
        pass

    def _gather_hashtags(self, tweet_id, last_time):
        """Sleep for the required time and then gather the hashtags from the
        replies

        :param tweet_id: Last tweet of the last thread where we will be
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

    def _send_story(self, thread):
        """Send the next story thread to the console

        :param thread: The next story thread to send
        :type thread: str
        :return: A random number to simulate twitter message ID
        :rtype: int
        """
        tweet_list = wrap(thread, 280)
        for tweet in tweet_list:
            print('====')
            print(tweet)
        # I'll want to keep track of the last tweet for the replies
        # Here we'll do a random number
        return randint(0, 1000000)

    def _gather_hashtags(self, tweet_id, last_time):
        """Instead of sleeping and then gathering the data from the twitter API
        we'll just gather them in the console.

        :param tweet_id: Last tweet of the last thread where we will be
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