#################
Twitter Game Book
#################

A Python program for running crowd sourced adventures as a bot on
`Twitter <https://twitter.com>`_ in a style similar to popular 1980s Game Books.
Stories are written on `Inklewriter <https://inklewriter.com>`_
 
Each story part will be tweeted as a thread. The final tweet in the thread will contain hashtags for the crowd sourced decisions.  Twitter users then reply to that tweet with their preferred hashtag.  After a period of a week, or shorter if things get popular, the hashtags in the reply will be parsed and counted.
 
Installation
============

Obtaining latest source code
----------------------------
::

    git clone https://github.com/djnrrd/twitter-game-book.git
    cd twitter-game-book

Alternatively, download the latest tar.gz source file from `the GitHub
repository <https://github.com/djnrrd/twitter-game-book/tree/master/dist>`_
::

    wget https://github.com/djnrrd/twitter-game-book/tree/master/dist/twitter
    -game-book-X-X-X.tar.gz
    tar -zxvf twitter-game-book-X-X-X.tar.gz
    cd twitter-game-book

Installing from source
----------------------
::

    # With pip (recommended)
    pip install .
    # Without pip, best used in a venv
    python3 setup.py install



Usage
=====

A JSON file from `Inklewriter <https://inklewriter.com>`_ is required.
When you share a story from Inklewriter, adding '.json' to the end of the URL
will give you the JSON file.  This URL may be passed as SOURCE to the command
line, or it can be downloaded locally and the path to the  local file provided
as SOURCE.

After posting a story thread, the bot will wait for PERIOD while users
respond with their preferred hashtags. PERIOD can be days, hours or minutes.

For testing dry runs, the --no-twitter option can be used to print the story
and capture "tweets" from the console.

To Do
=====
* Log into Twitter
* Send a tweet
* Send a thread
* Read replies to tweet
* Parse hashtags in replies

Change Log
==========

* 0.0.2 - Added functionality to force administrator choice of a hashtag, in
  case any trolls attempt to hijack the thread into loops
* 0.0.1 - First properly packaged version with working setup.py but still no
  twitter access

About Inklewriter JSON files
============================
 
JSON files from inklewood have the following structure:
::

    { "title":  "str",
      "data":  {
        "stitches": {},
        "initial": "str",
        "optionMirroring":  true,
        "allowCheckpoints": true,
        "editorData": {
          "playPoint": "str",
          "libraryVisible": true,
          "authorName": "str",
          "textSize": 0
        }
      }
    }

Stitches is a dictionary object that has been indexed by keys generated from
the first few words of each stitch.  Each stitch is a further dictionary, containing one list with the key "content".
::

    { "stitchKeyFro":  {
        "content": [
          "str",
          {}
        ]
      }
    }

Every content list starts with the story text. All other dictionaries are
optional.
::

    [
      {"pageNum": 0},
      {"page_label": "str"},
      {"divert": "str"},
      {"option": "str",
        "linkPath": "str",
        "ifConditions": [
          {"ifCondition": "str"}
        ],
        "notIfConditions": [
          {"notIfCondition": "str"}
        ]
      },
      {"flagName": "str"},
      {"ifCondition": "str"},
      {"notIfCondition": "str"}
    ]

If there are no divert or option objects, then you have reached an ending
notIfConditions and ifConditions appear to be a logical AND with no
duplication allowed. I think that's all the important ones for now.