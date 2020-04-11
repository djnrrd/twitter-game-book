import logging
import json
from textwrap import wrap
# Get the log into this namespace
logger = logging.getLogger('twgamebook')

class twgbStitch(object):
    """An object for managing the individual stitches of the story
    """

    def __init__(self, key, stitch):
        """Generate a twgbSwitch object from the source JSON

        :param key: The switch key from the source JSON
        :type key: str
        :param stitch: The switch data
        :type stitch: dict
        """
        logger.debug(f"Building switch obect {key}")
        self.key = key
        self.content = stitch['content'][0]
        self.divert = ''
        self.options = []
        self.flagNames = []
        self.pageNum = 0
        self.pageLabel = ''
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
                self.flagNames.append(option['flagName'])
            if 'pageNum' in option:
                logger.debug(f"Adding pageNum {option['pageNum']}")
                self.pageNum = option['pageNum']
            if 'pageLabel' in option:
                logger.debug(f"Adding pageLabel {option['pageLabel']}")
                self.pageLabel = option['pageLabel']

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
                source_data = self.load_http_json(source)
            else:
                source_data = self.load_local_json(source)
            if 'title' and 'data' in source_data:
                self.title = source_data['title']
                self.author = source_data['data']['editorData']['authorName']
                self.initial = source_data['data']['initial']
                self.stitches = self.load_stitches(source_data['data'][
                                                      'stitches'])
                self.flags = []
            else:
                logger.warning('Did not find expected Inklewriter JSON object')
                raise ValueError('Expected Inklewriter JSON object')
        else:
            raise KeyError('Expected string object as source')

    def load_http_json(self, source_url):
        """Get the source file from the internet

        :param source_url:
        :type source_url: str
        :return: Parsed JSON object
        """
        logger.debug(f"{source_url} provided as URL")
        logger.warning('Currently does not support HTTP')
        return False

    def load_local_json(self, source_file):
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

    def load_stitches(self, stitches):
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

    def get_stitch(self, key):
        """Return an individual stitch by it's key
        :param key: The key for the stitch to return
        :type key: str
        :return: The individual stitch
        :rtype: twgbStitch
        """
        stitch = [x for x in self.stitches if x.key == key]
        return stitch.pop()

    def read_options(self, options):
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
            # assume true unless the conditions tell us otherwise
            if_result = True
            not_if_result = True
            # Check of ifConditions
            if option['ifConditions']:
                # Get a list of all the flags for the ifcondition
                if_conds = [x['ifCondition'] for x in option['ifConditions']]
                # Check that all the ifConds exist in the game flags
                if_result = all(item in if_conds for item in self.flags)
            # Check for noIfConditions
            if option['notIfConditions']:
                # Get a list of the flag strings in the condition
                not_if_conds = [x['notIfCondition'] for x in option[
                    'notIfConditions']]
                # Check if all the notIfConds are not in game flags
                not_if_result = all(item not in not_if_conds for item in \
                        self.flags)
            if if_result and not_if_result:
                filtered_options.append(option)
        # Filtering done are we left with only one option? If we're left with
        # none we've broken the game and it's likely broken on inklewriter as
        # well
        if len(filtered_options) == 1:
            pass
            next_key = filtered_options[0]['linkPath']
            return self.get_stitch(next_key)
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

    def read_section(self, start_key='', ret_list=[]):
        """Read a section of the game until options or an ending is found

        :param start_key: The key for the starting stitch of the story. Leaving
            this blank will start the story from the beginning
        :type start_key: str
        :param ret_list: The cumulative previously returned thread, used in
            recursion
        :type ret_list: list
        :return: A list of tweets made up of all the stitches for this section.
        :rtype: list
        """
        # ret_list isn't being cleared when the method finishes, leading to
        # subsequent calls being a cumulative version of the results must be a
        # pythonic quirk I need to learn more about.
        if not ret_list:
            ret_list = []
        if not start_key:
            start_key = self.initial
        logger.debug(f"using Stitch ID {start_key}")
        stitch = self.get_stitch(start_key)
        # split the output to fit in 280 characters for twitter
        ret_list += wrap(stitch.content, 280)
        # Update game flags
        self.flags += stitch.flagNames
        # Now look if we need to keep going to the next piece
        if stitch.divert:
            return self.read_section(stitch.divert, ret_list)
        # Or generate our options, there shouldn't be both
        elif stitch.options:
            logger.info(f"{stitch.key} - {json.dumps(self.flags)}")
            option_tweets = self.read_options(stitch.options)
            if isinstance(option_tweets, twgbStitch):
                return self.read_section(option_tweets.key, ret_list)
            else:
                ret_list += option_tweets
                return ret_list
        # Otherwise we've reached an ending
        else:
            ret_list.append(f"Thank you for playing {self.title} by {self.author}")
            return ret_list


