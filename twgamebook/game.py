import logging
import json
from textwrap import wrap
import re
# Get the log into this namespace
logger = logging.getLogger('twgamebook')

class twgbStitch(object):
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

class twGameBook(object):
    """An object for loading JSON files from inklewriter.com
    """

    def __init__(self, source):
        """Build the twgamebook object

        :param source_file: The file path or URL to the source text
        :type source_file: str"""
        if isinstance(source, str):
            if source[0:7] == 'http://':
                source_data = self.__load_http_json(source)
            else:
                source_data = self.__load_local_json(source)
            if 'title' and 'data' in source_data:
                self.title = source_data['title']
                self.author = source_data['data']['editorData']['authorName']
                self.initial = source_data['data']['initial']
                self.stitches = self.__load_stitches(source_data['data'][
                                                      'stitches'])
                self.flags = []
            else:
                logger.warning('Did not find expected Inklewriter JSON object')
                raise ValueError('Expected Inklewriter JSON object')
        else:
            raise KeyError('Expected string object as source')

    def __load_http_json(self, source_url):
        """Get the source file from the internet

        :param source_url:
        :type source_url: str
        :return: Parsed JSON object
        """
        logger.debug(f"{source_url} provided as URL")
        logger.warning('Currently does not support HTTP')
        return False

    def __load_local_json(self, source_file):
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

    def __load_stitches(self, stitches):
        """Generate a list of twgbStitch objects

        :param stitches: Dictionary of stitches from the JSON source file
        :type stitches: dict
        :return: List of twgbSwitch objects
        :rtype: list
        """
        ret_list = []
        for key in stitches:
            ret_list.append(twgbStitch(key, stitches[key]))
        return ret_list

    def __get_stitch(self, key):
        """Return an individual stitch by it's key
        :param key: The key for the stitch to return
        :type key: str
        :return: The individual stitch
        :rtype: twgbStitch
        """
        stitch = [x for x in self.stitches if x.key == key]
        if stitch:
            return stitch.pop()
        else:
            return None

    def __read_options(self, options):
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
                if_conditions = [x['ifCondition'] for x in option['ifConditions']]
            else:
                if_conditions = []
            if option['notIfConditions']:
                not_if_conditions = [x['notIfCondition'] for x in option[
                'notIfConditions']]
            else:
                not_if_conditions = []
            if self.__pass_conditions(if_conditions, not_if_conditions):
                filtered_options.append(option)
        # Filtering done are we left with only one option? If we're left with
        # none we've broken the game and it's likely broken on inklewriter as
        # well
        if len(filtered_options) == 1:
            pass
            next_key = filtered_options[0]['linkPath']
            return self.__get_stitch(next_key)
        else:
            # Let's go!
            ret_list = []
            end_string = 'Should we:\n\n'
            for option in filtered_options:
                # Make sure we haven't exceeded an individual tweet
                if len(end_string) + len(option['option']) > 280:
                    ret_list.append(end_string)
                    end_string = ''
                end_string += f"* {option['option']}\n"
            # One more check for the foot text
            if len(end_string) +  49 > 280:
                ret_list.append(end_string)
                end_string = ''
            end_string += '\nReply to this tweet with your preferred Hashtag'
            ret_list.append(end_string)
            return ret_list

    def __pass_conditions(self, if_conditions=[], not_if_conditions=[]):
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

    def read_section(self, start_key='', _ret_list=[]):
        """Read a section of the game until options or an ending is found

        :param start_key: The key for the starting stitch of the story. Leaving
            this blank will start the story from the beginning
        :type start_key: str
        :param _ret_list: The cumulative previously returned thread, used in
            recursion
        :type _ret_list: list
        :return: A list of tweets made up of all the stitches for this section.
        :rtype: list
        """
        # _ret_list isn't being cleared when the method finishes, leading to
        # subsequent calls being a cumulative version of the results. Must be a
        # pythonic quirk I need to learn more about.
        if not _ret_list or not isinstance(_ret_list, list):
            _ret_list = []
        if not start_key or not isinstance(start_key, str):
            start_key = self.initial
        logger.debug(f"using Stitch ID {start_key}")
        stitch = self.__get_stitch(start_key)
        if stitch:
            # Update game flags
            self.flags += stitch.flag_names
            # Check if we display this stitch:
            if self.__pass_conditions(stitch.if_conditions,
                                      stitch.not_if_conditions):
                # split the output to fit in 280 characters for twitter
                _ret_list += wrap(stitch.content, 280)
            # Now look if we need to keep going to the next piece
            if stitch.divert:
                return self.read_section(stitch.divert, _ret_list)
            # Or generate our options, there shouldn't be both
            elif stitch.options:
                logger.info(f"{stitch.key} - {json.dumps(self.flags)}")
                option_tweets = self.__read_options(stitch.options)
                if isinstance(option_tweets, twgbStitch):
                    return self.read_section(option_tweets.key, _ret_list)
                else:
                    _ret_list += option_tweets
                    return _ret_list
            # Otherwise we've reached an ending
            else:
                logger.info(f"GAMEEND - {self.title}")
                _ret_list.append(f"Thank you for playing {self.title} by {self.author}")
                return _ret_list
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
            stitch = self.__get_stitch(key)
            if stitch:
                ret_list = []
                pattern = re.compile('#[0-9a-zA-Z]+')
                for option in stitch.options:
                    hash_tags = pattern.findall(option['option'])
                    stitch_key = option['linkPath']
                    if len(hash_tags) == 1:
                        ret_list.append((hash_tags[0], stitch_key))
                    else:
                        logger.warning(f"Expected to find 1 hashtag in "
                                       f"{option['option']}")
                        raise ValueError('Expected to find 1 hashtag')
                return ret_list
            else:
                logger.warning(f"Could not find {key} in the game")
                raise KeyError(f"Could not find {key} in the game")
        else:
            raise KeyError('string expected as key')
