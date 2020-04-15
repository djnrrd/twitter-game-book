#Twitter Game Book

A Python program for running crowd sourced adventures as a bot on Twitter.com
 in a style similar to popular 1980s Game Books.
 
 Each story part will be tweeted as a thread. The final tweet in the thread
  will contain hashtags for the crowd sourced decisions.  Twitter users then
   reply to that tweet with their preferred hashtag.  After a period of a
    week, or shorter if things get popular, the hashtags in the reply will be
     parsed and counted
 
 
 
 ##To Do
 * Log into Twitter
 * Send a tweet
 * Send a thread
 * Read replies to tweet
 * Parse hashtags in replies
 * ~~Determine adventure file formatting~~
   * ~~Inklewriter.com does JSON so testing with this.~~
 * ~~Load adventure~~
    * ~~By File~~
    * ~~By HTTP~~
 * ~~Parse adventure file~~
 * ~~Print required sections~~
    * ~~Create cumulative text from diverts~~
    * ~~Add options to the end of the print~~
    * ~~Check conditions on stitches~~
    * ~~Gracefully end the session~~
    * ~~Log last position~~ 
 * ~~Sleep app for required time~~
 * ~~Wake from sleep~~
 * ~~Load last position from log~~
 * ~~Update game flags from log~~
 * ~~Check last position for required hashtags~~
    * ~~Game object done~~
    * ~~Wrapper code needed~~
 * ~~Compare hashtags from twitter and choose new starting position~~
 * ~~Use log to determine position at startup and set timer~~
 * Glue that all together ????
 
 ## About Inklewriter JSON files
 
JSON files from inklewood have the following structure:

```JSON
{ "title":  "str",
  "data":  {
    "stitches": {},   # Documented below
    "initial": "str", # The key of the starting stitch
    "optionMirroring":  bool, 
    "allowCheckpoints": bool,
    "editorData": {
      "playPoint": "str", # 
      "libraryVisible": bool,
      "authorName": "str",
      "textSize": int
    }
  }
}
```

Stitches is a dictionary object that has been indexed by keys generated from
 the first few words of each stitch.  Each stitch is a further dictionary
 , containing one list with the key "content".  

```JSON
{ "stitchKeyFro":  {
    "content": [
      "str",          # The actual story text
      {}              # Optional Dictionary objects documented below 
    ]
  }
}
```

Every content list starts with the story text. All other dictionaries are
 optional.

```JSON
{"pageNum": int}                # Section page number
{"page_label": "str"}            # Section label
{"divert": "str"}               # Key to the next Stitch, direct link
{"option": "str",               # Text for the option
  "linkPath": "str",            # Key to the next Stitch
  "ifConditions": [
    {"ifCondition": "str"}      # List of conditions for showing the option  
  ] or None,   
  "notIfConditions": [
    {"notIfCondition": "str"}   # List of negative conditions
  ] or None
}
{"flagName": "str"}             # Flags to keep track of for ifConditions
{"ifCondition": "str"}          # List of conditions for showing the stitch
{"notIfCondition": "str"}       # List of negative conditions
```

If there are no divert or option objects, then you have reached an ending
 notIfConditions and ifConditions appear to be a logical AND with no
 duplication allowed. I think that's all the important ones for now.