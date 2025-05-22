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

## TODO
figure out new line
look at bindings for possibly useful stuff
think about tables
get center
get other old attributes like indent
test with adobe 10k pdf

## Issues
* Adobe PDF encodings return weird characters.

## Misc
* Estimating crude measure of font-size from bounding box.