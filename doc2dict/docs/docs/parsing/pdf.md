# PDF

???+ warning "Very Early Stage"
    This code is in a very early stage.

## Quickstart
```
# Load your pdf file
with open('apple_10k_2024.pdf','rb') as f:
    content = f.read()

# Convert to dictionary
dct = pdf2dict(content,mapping_dict=None)
```


## Benchmarks
* About 200 pages per second single threaded.

???+ warning "multithreading"
    pdf2dict can't be run multithreaded due to the limitations of pypdfium2


## Compatibility
Requires pdfs with underlying text structure so no scans yet. 

`convert_scan_to_instructions` would be fairly straightforward to implement. Font-size can be inferred from bounding boxes, as can line alignment. Rotation probably won't be an issue for decent scans like the ones submitted to the SEC.

The issue is performance.

The point of `doc2dict` is mostly that it's fast. Local OCR such as pytesseract would put a hard cap of 10 pages per second.

This is too slow to be useful for my use-case. Here's a benchmark.

**Convert all 2024 Annual Report to Shareholders to dict form**
2000 a year * mean 50 pages / 200 pages per second = 500 seconds = ~ 10 minutes. (PDF Parser)

Where as a scan parser would take at least 200 minutes ~ 3 hours.

I think the solution will be to write a scan parser that takes input of bounding boxes/ minimum features required as input. Users can then use their preferred OCR - e.g. local, Google, AWS, etc for the slow part.

## TODO
think about tables
get center
get other old attributes like indent

## Issues
* Adobe PDF encodings return weird characters.
