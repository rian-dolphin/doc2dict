# doc2dict (NOT READY FOR PUBLIC USE YET)

Convert HTML, XML, and PDFs into dictionaries using an algorithimic approach, e.g. [unstructured.io](https://unstructured.io/) but open-source and without LLMs.

Parsers
1. HTML Parser (WIP)
2. XML Parser (WIP)
3. PDF/IMAGE Parser (Planned)

## Installation
```
pip install doc2dict
```

## Quickstart
```
# something about xml, html here showcasing viz as well as parsing
```

### General Strategy
1. Reduce complicated underlying stucture to only necessary components
2. Use rules to map reduced form into a nested dictionary 
3. Apply mapping dicts to provide fine-grained control over dictionary names

### Add-ons
* Mapping dicts for every SEC form and attachment (WIP)

### Speed (WIP)
* Target - 10,000 pages per second for HTML parser
* Will rewrite in Cython or C bindings if better performance needed.

### Current Benchmarks
* Bumble 10k (100 pages), 50ms to load, 80ms to iterate through

### TODO
* rebuild engine. to handle css, html. start from scratch ish, but explain what general features to add
* then add them in, bold, italic, underline (and derivatives from e.g. tables etc)
* add height of READABLE not font
* add indent
* then move to mapping rules
* then move to mapping dict
