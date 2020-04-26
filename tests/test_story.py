from unittest import TestCase
from twgamebook import story
import json

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
        self.assertRaises(json.JSONDecodeError, story.TWGBStory, 'test_inputs/bad_input.json')

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