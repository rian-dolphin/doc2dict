# Overview

## Mapping Dicts
<b>doc2dict</b> makes extensive use of mapping dicts. These are rules that do...

## XML Parsing

XML Parsing is mostly done using Martin Blech's fantastic [xmltodict](https://github.com/martinblech/xmltodict). The resulting dictionary is then processed with a mapping dict.

## TXT Parsing

Text Parsing is difficult due to lack of detail. We use mapping dicts here to do stuff like use regex to say 'item 1' should be one level from top.

## HTML Parsing

1. Extract information and construct a list of in with text and useful info like `bold` and `font size`
2. Use a rules to convert into a dictionary format with processed tables and the like
3. Use a mapping dict for standardization - like in SEC 10-Ks

Also good visualization software so we can debug easy.

## PDF Parsing

Will be implemented later.
