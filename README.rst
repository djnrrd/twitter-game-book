#Twitter Game Book

A Python program for running crowd sourced adventures as a bot on
`Twitter <https://twitter.com>`__ in a style similar to popular 1980s
Game Books. Stories are written on
`Inklewriter <https://inklewriter.com>`__

Each story part will be tweeted as a thread. The final tweet in the
thread will contain hashtags for the crowd sourced decisions. Twitter
users then reply to that tweet with their preferred hashtag. After a
period of a week, or shorter if things get popular, the hashtags in the
reply will be parsed and counted.

##Installation

##To Do \* Log into Twitter \* Send a tweet \* Send a thread \* Read
replies to tweet \* Parse hashtags in replies \* [STRIKEOUT:Determine
adventure file formatting] \* [STRIKEOUT:Inklewriter.com does JSON so
testing with this.] \* [STRIKEOUT:Load adventure] \* [STRIKEOUT:By File]
\* [STRIKEOUT:By HTTP] \* [STRIKEOUT:Parse adventure file] \*
[STRIKEOUT:Print required sections] \* [STRIKEOUT:Create cumulative text
from diverts] \* [STRIKEOUT:Add options to the end of the print] \*
[STRIKEOUT:Check conditions on stitches] \* [STRIKEOUT:Gracefully end
the session] \* [STRIKEOUT:Log last position] \* [STRIKEOUT:Sleep app
for required time] \* [STRIKEOUT:Wake from sleep] \* [STRIKEOUT:Load
last position from log] \* [STRIKEOUT:Update game flags from log] \*
[STRIKEOUT:Check last position for required hashtags] \* [STRIKEOUT:Game
object done] \* [STRIKEOUT:Wrapper code needed] \* [STRIKEOUT:Compare
hashtags from twitter and choose new starting position] \*
[STRIKEOUT:Use log to determine position at startup and set timer] \*
Glue that all together ????

## About Inklewriter JSON files

JSON files from inklewood have the following structure:

.. code:: json

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

Stitches is a dictionary object that has been indexed by keys generated
from the first few words of each stitch. Each stitch is a further
dictionary , containing one list with the key “content”.

.. code:: json

   { "stitchKeyFro":  {
       "content": [
         "str",          
         {}               
       ]
     }
   }

Every content list starts with the story text. All other dictionaries
are optional.

.. code:: json

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

If there are no divert or option objects, then you have reached an
ending notIfConditions and ifConditions appear to be a logical AND with
no duplication allowed. I think that’s all the important ones for now.
