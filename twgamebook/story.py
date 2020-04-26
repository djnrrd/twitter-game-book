import json
import re

import requests

from twgamebook.game import LOGGER


class TWGBStitch(object):
    """An object for managing the individual story stitches.

    A stitch is a paragraph of text from inklewriter.com and the relevant
    options for branched story telling.  Each stitch will have a unique key
    as a reference and the text of the paragraph.

    :param str key: The stitch key from the inklewriter source JSON
    :param dict stitch: The stitch data from the inklewriter source JSON

    :cvar str key: Unique key for this stitch
    :cvar str content: Text for this stitch
    :cvar str divert: Key for the next stitch in the story. Only provided if
        there are no options and the story has not ended.
    :cvar list options: A list of possible options to follow after this stitch
    :cvar list flag_names: A list of flags that should be appended to the
        story when this stitch is loaded
    :cvar list if_conditions: A list of flags that must *all* be logged in the
        story for this stitch to be visible
    :cvar list not_if_conditions: A list of flags that must not be logged in
        the story for the stitch to be visible.
    :cvar int page_num: The page number from inklewriter
    :cvar str page_label: The title for this page or section of the story on
        inklewriter
    """

    def __init__(self, key, stitch):
        """Object init
        """
        LOGGER.debug(f"Building switch obect {key}")
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
                LOGGER.debug(f"Adding divert to {option['divert']}")
                self.divert = option['divert']
            if 'option' in option:
                LOGGER.debug(f"Adding options {option}")
                self.options.append(option)
            if 'flagName' in option:
                LOGGER.debug(f"Adding flag {option['flagName']}")
                self.flag_names.append(option['flagName'])
            if 'pageNum' in option:
                LOGGER.debug(f"Adding page_num {option['pageNum']}")
                self.page_num = option['pageNum']
            if 'pageLabel' in option:
                LOGGER.debug(f"Adding page_label {option['pageLabel']}")
                self.page_label = option['pageLabel']
            if 'ifCondition' in option:
                LOGGER.debug(f"Adding if_condition {option['ifCondition']}")
                self.if_conditions.append(option['ifCondition'])
            if 'notIfCondition' in option:
                LOGGER.debug(f"Adding not_if_condition"
                             f" {option['notIfCondition']}")
                self.not_if_conditions.append(option['notIfCondition'])

    def __repr__(self):
        return self.key

    def __str__(self):
        return self.key


class TWGBStory(object):
    """An object for loading JSON files from inklewriter.com and managing the
    story and it's stitches

    :param str source_file: The file path or URL to the source text

    :raises KeyError: if a string is not provided to the constructor
    :raises ValueError: if the source file is not an inklewriter.com JSON
        object or if the local file could not be found
    :raises ConnectionError: if there are any network issues connecting to
        inklewriter.com
    :raises Timeout: if there is a network timeout connecting to inklewriter.com
    :raises TooManyRedirects: if there are too many redirects trying to
        retrieve the JSON file from inklewriter.com
    :raises HTTPError: if any HTTP code other than 200 is received from
        inklewriter.com
    :raises json.JSONDecodeError: if there was an issue decoding the JSON file

    :cvar str title: The title of this story
    :cvar str author: The story's author
    :cvar str initial: The initial stitch key to start the story from
    :cvar list stitches: The list of stitches that make up the story
    :cvar list flags: The list of flags encountered during the story's
        progress
    """

    def __init__(self, source):
        """Build the twgamebook object"""
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
                LOGGER.warning('Did not find expected Inklewriter JSON object')
                raise ValueError('Expected Inklewriter JSON object')
        else:
            raise KeyError('Expected string object as source')

    def _load_http_json(self, source_url):
        """Get the source file from the internet

        :param str source_url:
        :return: Parsed JSON object
        """
        LOGGER.debug(f"{source_url} provided as URL")
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
            LOGGER.debug(f"Attempting to open {source_file}")
            with open(source_file, 'r') as f:
                source_json = json.loads(f.read())
        except FileNotFoundError:
            LOGGER.warning(f"Could not open {source_file}")
            raise ValueError(
                f"Source file {source_file} must either be a local "
                f"file or HTTP file")
        except json.JSONDecodeError as e:
            LOGGER.warning(f"Could not parse JSON from {source_file}")
            raise json.JSONDecodeError(f"Could not parse JSON from "
                                       f"{source_file}", e.doc, e.pos)
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
        """Generate the stitch endings when options are present on the stitch

        :param options: The list of options from the stitch
        :type options: list
        :return: List of stitch ending tweets
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
            return [ret_str]

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

    def get_section(self, start_key='', _ret_list=[]):
        """Read a section of the game until options or an ending is found

        :param start_key: The key for the starting stitch of the story. Leaving
            this blank will start the story from the beginning
        :type start_key: str
        :param _ret_list: The cumulative previously returned stitch, used in
            recursion
        :type _ret_list: str
        :return: A list of paragraphs with the options as the final paragrah
            for this section
        :rtype: list
        """
        # _ret_list isn't being cleared when the method finishes, leading to
        # subsequent calls being a cumulative version of the results. Must be a
        # pythonic quirk I need to learn more about.
        if not _ret_list or not isinstance(_ret_list, list):
            _ret_list = []
        if not start_key or not isinstance(start_key, str):
            start_key = self.initial
        LOGGER.debug(f"using Stitch ID {start_key}")
        stitch = self._get_stitch(start_key)
        if stitch:
            # Update game flags
            self.flags += stitch.flag_names
            # Check if we display this stitch:
            if self._pass_conditions(stitch.if_conditions,
                                     stitch.not_if_conditions):
                _ret_list += [stitch.content]
            # Now look if we need to keep going to the next piece
            if stitch.divert:
                return self.get_section(stitch.divert, _ret_list)
            # Or generate our options, there shouldn't be both
            elif stitch.options:
                # Write the option key and flags to the log
                LOGGER.info(f"{stitch.key} - {json.dumps(self.flags)}")
                # Format the options, if there aren't any the next stitch
                # will be returned instead
                option_tweets = self._get_options(stitch.options)
                if isinstance(option_tweets, TWGBStitch):
                    return self.get_section(option_tweets.key, _ret_list)
                else:
                    _ret_list += option_tweets
                    return _ret_list
            # Otherwise we've reached an ending
            else:
                # Write that we ended to the log
                LOGGER.info(f"GAMEEND {self.title}")
                _ret_list += [f"Thank you for playing {self.title} by" \
                            f" {self.author}"]
                return _ret_list
        else:
            LOGGER.warning(f"Could not find {start_key} in the game")
            raise KeyError(f"Could not find {start_key} in the game")

    def get_hashtags(self, key):
        """Get the hashtags associated with the options

        :param key: The key of the stitch containing the options
        :type key: str
        :return: A List of hashtags and associated stitch keys
        :rtype: list
        """
        if isinstance(key, str):
            LOGGER.debug(f"Looking for hashtags in {key}")
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
                        LOGGER.warning(f"Expected to find 1 hashtag in "
                                       f"{option['option']}")
                        raise ValueError('Expected to find 1 hashtag')
                return ret_dict
            else:
                LOGGER.warning(f"Could not find {key} in the game")
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