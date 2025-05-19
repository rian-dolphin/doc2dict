# High Speed Document Algorithmic Parsing

## Abstract
Parsing documents that are human readable into machine readable form is difficult due to under the hood variation. Here is my attempt at providing a fast, robust generalized approach, that can be easily modified to account for variation in documents.

<div style="">
  <a href="javascript:window.print()" class="md-button md-button--primary" style="padding: 0.3rem 0.6rem; font-size: 0.8rem;">Download as PDF</a>
</div>

???+ note "Caveats"
    This is not meant to be a perfect parsing approach. It's meant to be a "good enough" approach that is fast enough to parse the entire SEC corpus on a personal laptop. This is also in an early stage - things will change.

???+ note "Terminology"
    I don't know the right words to use. If you do, please [email me](mailto:johnfriedman@datamule.xyz) and/or bully me into correcting the terminology.


## General

### Approach
1. Convert messy document into a simple list of instructions.
2. Convert the list of instructions into dictionary using a set of rules that can be easily tailored for the document.

The idea here is to turn a complex problem that is hard to solve, into a simple problem, that is easy to solve.
* Nested html is hard to understand -> the same html in list form is easy
* Raw pdfs are hard to understand -> the same pdf in list form is easy

We can then convert from the (flat) list form into a nested dictionary by using simple rules like "bigger headers have higher nesting" as well as specify where certain headers go - "item 1a risk factors should be nested under part i".

This also makes the parsing easier to modify for less technical users. A grad student in economics is unlikely to be able to modify the walk through a html document to properly account for style inheritance, but likely can modify rules such as "ignore italics for header selection".

#### Examples
Instructions List:
```
[{'text': 'PART I', 'text-style': 'all_caps', 'left-indent': 8.0, 'font-size': 13.33, 'text-center': True, 'bold': True}]
[{'text': 'ITEM 1. BUSINESS', 'text-style': 'all_caps', 'left-indent': 8.0, 'font-size': 15.995999999999999, 'text-center': True, 'bold': True}]
[{'text': 'GENERAL', 'text-style': 'all_caps', 'left-indent': 8.0, 'font-size': 13.33, 'text-center': True, 'underline': True}]
[{'text': 'Embracing Our Future', 'left-indent': 8.0, 'font-size': 13.33, 'bold': True}]...
```

Dictionary
```
        "37": {
            "title": "PART I",
            "standardized_title": "parti",
            "class": "part",
            "contents": {
                "38": {
                    "title": "ITEM 1. BUSINESS",
                    "standardized_title": "item1",
                    "class": "item",
                    "contents": {
                        "39": {
                            "title": "GENERAL",
                            "standardized_title": "",
                            "class": "predicted header",
                            "contents": {
                                "40": {
                                    "title": "Embracing Our Future",...
```



### Mapping Dictionaries
I call the set of rules used to convert the list of instructions into a dictionary a "mapping dict". The idea is that a less technical user who will have trouble tweaking the engine can easily modify a list of rules that tweak the output.

#### Example
```
dict_10k_html = {
    ('part',r'^part\s*([ivx]+)$') : 0,
    ('signatures',r'^signatures?\.*$') : 0,
    ('item',r'^item\s*(\d+)\.?([a-z])?') : 1,
}
```

The above mapping dict tells the parser to assign class 'part' to predicted headers and assign hierarchy '0' or root level. It then uses the capture group `([ivx]+)` and the class to determine the standarized_title.

## HTML

The basic html approach has already been implemented. Ballpark speed is about 500 pages per second on my two year old personal laptop.

### Approach

1. Iterate through the html file, keeping track of attributes that apply for each text node, with special handling for tables to create the instructions list. Output each text node as an instruction on the same line if the two text nodes visually appear on the same line.
2. For the instructions list, determine which instructions are likely to be headers. If an instruction is a header, determine hierarchy with the aid of a mapping dict if present.

### Tables

1. Construct a matrix with each cell representing a cell in the table
2. If a cell spans multiple rows or columns, duplicate the cell in the matrix
3. Remove rows and columns that are considered empty - e.g. have only empty characters
4. Remove rows and columns that contain no unique information - e.g. if a column is a subset of another column, remove it.

TODO

* Currently removes unmatched parenthesis columns, in the future will merge them
* Currently does not handle indents - many tables can be split into multiple tables using information from indents

???+ note "Goal"
    The goal here is not to perfectly parse tables. We can get close, but often the information for html tables is above the table in a seperate block. 

### Visualization

Visualization is important for both the instructions_list stage and the final dict stage. Visualization lets users quickly debug whether the parser is working as expected, and what to tweak.