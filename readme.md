# doc2dict (NOT READY FOR PUBLIC USE YET)

Convert HTML, XML, and PDFs into dictionaries using an algorithmic approach.

Parsers
1. HTML Parser (WIP)
2. XML Parser - please use Martin Blech's excellent xmltodict. doc2dict's xml2dict is currently a mess.
3. PDF/IMAGE Parser (Planned)

## Installation
```
pip install doc2dict
```

## Quickstart
```
from doc2dict import html2dict

with open('tesla10k.txt','r') as f:
    content = f.read()
html_dict = html2dict(content,mapping_dict=None)
```