# HTML

## Quickstart
```
# Load your html file
with open('apple_10k_2024.htm','r') as f:
    content = f.read()

# Convert to dictionary
dct = html2dict(content,mapping_dict=None)
```

### Example 
```
...
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
                            "title": "Embracing Our Future",
...
"292": {
        "table": [
            [
                "Name",
                "Age",
                "Position with the Company"
            ],
            [
                "Satya Nadella",
                "56",
                "Chairman and Chief Executive Officer"
            ],
...
```
    


## Tweaking the engine for your use case

???+ note "I will make this section better soon"
    I just want to get the basic docs out!

### Debugging
```
from doc2dict import convert_html_to_instructions, convert_instructions_to_dict, visualize_instructions, visualize_dict

# load your html file
with open('tesla10k.htm','r') as f:
    content = f.read()

# convert html to a series of instructions
instructions = convert_html_to_instructions(content)

# visualize the conversion
visualize_instructions(instructions)

# convert instructions to dictionary
dct = html2dict(content,mapping_dict=None)

# visualize dictionary
visualize_dict(dct)
```

### Writing your own mapping dictionaries

???+ warning "Experimental"
    If you write a mapping dict, and I change something so it stops working - please [email me](mailto:johnfriedman@datamule.xyz).

Mapping dicts currently work by specifying the class of the section header: `part`, regex for section header `r'^part\s*([ivx]+)$'` where the capture group `([ivx]+)` and class `part` determine the `standardized_title`, and the level, where `0` is the root.

In this example, `items` will always be nested under `parts`.
```
dict_10k_html = {
    ('part',r'^part\s*([ivx]+)$') : 0,
    ('signatures',r'^signatures?\.*$') : 0,
    ('item',r'^item\s*(\d+)\.?([a-z])?') : 1,
}
```
