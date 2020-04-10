import logging
import json

# Get the log into this namespace
logger = logging.getLogger('twgamebook')

class twGameBook(object):
    """An object for loading JSON files from inklewriter.com
    """

    def __init__(self, source):
        """Build the twgamebook object

        :param source_file: The file path or URL to the source text
        :type source_file: str"""
        if isinstance(source, str):
            if source[0:7] == 'http://':
                self.get_http_json(source)
            else:
                self.get_local_json(source)
        else:
            raise KeyError('Expected string object as source')

    def get_http_json(self, source_url):
        """Get the source file from the internet

        :param source_url:
        :type source_url: str
        """
        logger.debug(f"{source_url} provided as URL")
        logger.warning('Currently does not support HTTP')

    def get_local_json(self, source_file):
        """Get the source file from local disk

        :param source_file: Path to the locally stored source file
        :type source_file: str
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
        self.load_game(source_json)

    def load_game(self, source_data):
        """Load the game into memory
        :param source_data: Source data parsed through json library
        :type source_data: dict
        """
        # Final check for the keys and then load everything into the object.
        if 'title' and 'data' in source_data:
            self.title = source_data['title']
            self.initial = source_data['data']['initial']
            self.stitches = source_data['data']['stitches']
            self.flags = []
        else:
            logger.warning('Did not find expected Inklewriter JSON object')
            raise ValueError('Expected Inklewriter JSON object')

    def read_section(self, start='', ret_str=''):
        """Read a section of the game until options or an ending is found

        :param start: The key for the starting stitch of the story. Leaving
            this blank will start the story from the beginning
        :type start: str
        :param ret_str: The cumulative previously returned string, used in
            recursion
        :type ret_str: str
        :return: The complete section of this game
        :rtype: str
        """
        if not start:
            start = self.initial
        logger.debug(f"using Stitch ID {start}")
        ret_str += self.stitches[start]['content'][0]
        # Get the keys of the dict objects and their index position in the
        # content list, a bit messy but a one off
        stitch_keys = {}
        for content in self.stitches[start]['content']:
            if isinstance(content, dict):
                for content_key in content:
                    stitch_keys[content_key] = self.stitches[start][
                                                   'content'].index(content)
        logger.debug(f"Found the following keys: {stitch_keys}")
        # Now look if we need to keep going to the next piece
        if 'divert' in stitch_keys:
            next = self.stitches[start]['content'][stitch_keys['divert']][
                'divert']
            ret_str += '\n\n'
            return self.read_section(next, ret_str)
        elif 'option' in stitch_keys:

        else:
            return ret_str
