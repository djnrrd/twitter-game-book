#Twitter Game Book

A Python program for running crowd sourced adventures as a bot on [Twitter](https://twitter.com) in a style similar to popular 1980s Game Books. Stories are written on [Inklewriter](https://inklewriter.com)
 
Each story part will be tweeted as a thread. The final tweet in the thread will contain hashtags for the crowd sourced decisions.  Twitter users then reply to that tweet with their preferred hashtag.  After a period of a week, or shorter if things get popular, the hashtags in the reply will be parsed and counted.
 
 ##Installation
  
   
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
```

Stitches is a dictionary object that has been indexed by keys generated from
 the first few words of each stitch.  Each stitch is a further dictionary
 , containing one list with the key "content".  

```JSON
{ "stitchKeyFro":  {
    "content": [
      "str",          
      {}               
    ]
  }
}
```

Every content list starts with the story text. All other dictionaries are
 optional.

```JSON
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
```

If there are no divert or option objects, then you have reached an ending
 notIfConditions and ifConditions appear to be a logical AND with no
 duplication allowed. I think that's all the important ones for now.