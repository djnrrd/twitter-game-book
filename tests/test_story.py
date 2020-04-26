from unittest import TestCase
from twgamebook import story
import json
import logging

# Setup the logger for unittests to write to
LOGGER = logging.getLogger('twgamebook')
LOGGER.setLevel(logging.INFO)
_LOG_FH = logging.FileHandler('twgamebook.log')
_LOG_FH.setLevel(logging.INFO)
_log_format = logging.Formatter('%(asctime)s - %(levelname)s - %(''message)s',
                                datefmt='%b %d %H:%M')
_LOG_FH.setFormatter(_log_format)
LOGGER.addHandler(_LOG_FH)


class TestTWGBStoryLocal(TestCase):

    def setUp(self):
        self.story = story.TWGBStory('test_inputs/good_input.json')


class TestTWGBStoryLive(TestCase):

    def setUp(self):
        self.story = story.TWGBStory(
            'https://www.inklewriter.com/stories/3198.json')


class TestTWGBStoryRaises(TestCase):

    def test_no_string(self):
        self.assertRaises(KeyError, story.TWGBStory, 000)

    def test_invalid_path(self):
        self.assertRaises(ValueError, story.TWGBStory, '/good_input.json')

    def test_bad_json(self):
        self.assertRaises(json.JSONDecodeError, story.TWGBStory,
                          'test_inputs/bad_input.json')


class TestTWGBStoryInit(TestTWGBStoryLocal):

    def test_initial_title(self):
        assert self.story.title == 'The Cave of Tests'
        print(f"Story title: {self.story.title}")

    def test_initial_author(self):
        assert self.story.author == 'DJ Nrrd'
        print(f"Story author: {self.story.author}")

    def test_initial_key(self):
        assert self.story.initial == 'youHaveDiscovere'
        print(f"Initial key: {self.story.initial}")

    def test_initial_stitches(self):
        assert isinstance(self.story.stitches, list)
        print(f"Stitches are type {type(self.story.stitches)}")

    def test_stitch_length(self):
        assert len(self.story.stitches) == 50
        print(f"There are {len(self.story.stitches)} stitches")

    def test_initial_flags(self):
        assert isinstance(self.story.flags, list)
        print(f"Flags are type {type(self.story.flags)}")

    def test_flag_length(self):
        assert len(self.story.flags) == 0
        print(f"There are {len(self.story.flags)} flags")

    def test_intial_object(self):
        assert isinstance(self.story, story.TWGBStory)
        print(f"Story object is {type(story.TWGBStory)}")


class TestTWGBStoryGetHashtags(TestTWGBStoryLocal):

    def test_get_hashtags(self):
        valid_hashtags = {'#LEFT': 'asYouCrawlThroug',
                          '#RIGHT': 'youCrawlThroughT',
                          '#FIRE': 'youFindASovereig'}
        assert self.story.get_hashtags('oppositeTheChamb') == valid_hashtags
        print(f"Valid hashtags: {self.story.get_hashtags('oppositeTheChamb')}")


class TestTWGBStoryGetSection(TestTWGBStoryLocal):

    def test_get_section_type(self):
        assert isinstance(self.story.get_section(), list)
        print(f"First section is type {type(self.story.get_section())}")

    def test_get_section_length(self):
        assert len(self.story.get_section()) == 4
        print(f"First section is len: {len(self.story.get_section())}")

    def test_get_section_log_written(self):
        section = self.story.get_section()
        with open('twgamebook.log', 'r') as f:
            logs = f.readlines()
        info_logs = [x for x in logs if 'INFO' in x]
        assert 'INFO - oppositeTheChamb - []' in info_logs[-1]
        print(f"Last log: {info_logs[-1]}")

    def test_get_section_flags_logged(self):
        self.story.flags.append('has_ring')
        section = self.story.get_section()
        with open('twgamebook.log', 'r') as f:
            logs = f.readlines()
        info_logs = [x for x in logs if 'INFO' in x]
        assert 'INFO - oppositeTheChamb - ["has_ring"]' in info_logs[-1]
        print(f"Last log: {info_logs[-1]}")

    def test_get_section_not_if_options(self):
        self.story.flags.append('has_ring')
        section = self.story.get_section()
        assert section[-1] == 'Should we:\n\n* Go #Left\n* Go ' \
                              '#Right\n\nReply to this tweet with your ' \
                              'preferred Hashtag'
        print(f"Last tweet: {section[-1]}")

    def test_get_section_if_options(self):
        self.story.flags.append('has_ring')
        section = self.story.get_section('youPushTheCrateA')
        assert section[-1] == 'Should we:\n\n* Tell her about the #tunnels\n* ' \
                              'Show her the #ring\n\nReply to this tweet with ' \
                              'your preferred Hashtag'
        print(f"Last tweet: {section[-1]}")

    def test_get_section_one_option(self):
        section = self.story.get_section('youPushTheCrateA')
        assert section[-1] == "Should we:\n\n* 'I don't believe you!' Head " \
                              "back #home\n* Accept your #fate\n\n" \
                              "Reply to this tweet with your preferred Hashtag"
        print(f"Last tweet: {section[-1]}")

    def test_get_section_if_stitch_type(self):
        self.story.flags +=['has_ring']
        section = self.story.get_section('youFindYourselfO')
        assert isinstance(section, list)
        print(f"If stitch section is type {type(self.story.get_section())}")

    def test_get_section_if_stitch_length(self):
        self.story.flags +=['has_ring']
        section = self.story.get_section('youFindYourselfO')
        assert len(section) == 7
        print(f"If stitch section len: {len(self.story.get_section('youFindYourselfO'))}")

    def test_get_section_if_not_stitch_type(self):
        self.story.flags +=['has_ring', 'gave_ring_away']
        section = self.story.get_section('youFindYourselfO')
        assert isinstance(section, list)
        print(f"If stitch section is type {type(self.story.get_section())}")

    def test_get_section_if_not_stitch_length(self):
        self.story.flags +=['has_ring',  'gave_ring_away']
        section = self.story.get_section('youFindYourselfO')
        assert len(section) == 6
        print(f"If stitch section len: {len(self.story.get_section('youFindYourselfO'))}")