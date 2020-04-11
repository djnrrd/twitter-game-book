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
        self.flagName = ''
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
                self.flagName = option['flagName']
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
        stitch = [x for x in self.stitches if x.key == key]
        return stitch.pop()

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
        if not start_key:
            start_key = self.initial
        logger.debug(f"using Stitch ID {start_key}")
        stitch = self.get_stitch(start_key)
        ret_list += wrap(stitch.content, 280)

        # Now look if we need to keep going to the next piece
        if stitch.divert:
            return self.read_section(stitch.divert, ret_list)
        elif stitch.options:
            return ret_list
        else:
            return ret_list

