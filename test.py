from selectolax.parser import HTMLParser
from doc2dict.doc2dict.html.convert_html_to_instructions import convert_html_to_instructions
from doc2dict.doc2dict.html.visualize_instructions import visualize_instructions
from doc2dict.doc2dict.html.convert_instructions_to_dict import convert_instructions_to_dict, tenk_mapping_dict, determine_levels, collapse_dict
from time import time
import webbrowser
import json


# Benchmark bottom 150ms

file_path=r'C:\Users\jgfri\OneDrive\Desktop\test\test\0000320193-24-000123\aapl-20240928.htm'
file_path = r"C:\Users\jgfri\OneDrive\Desktop\test\test\0000950170-24-087843\msft-20240630.htm"
#file_path = r"C:\Users\jgfri\OneDrive\Desktop\test.html"
 

start = time()
with open(file_path, 'r', encoding='utf-8') as f:
    parser = HTMLParser(f.read())

print("load time:", time()-start)

start = time()
body = parser.body
instructions = convert_html_to_instructions(body)
print("convert to instructions time:", time()-start)

with open('instructions2.txt', 'w', encoding='utf-8') as f:
    for instruction in instructions:
        f.write(str(instruction) + '\n')

# webbrowser.open(file_path)
# visualize_instructions(instructions)
levels = determine_levels(instructions, tenk_mapping_dict)
with open('levels.txt', 'w', encoding='utf-8') as f:
    for level in levels:
        f.write(str(level) + '\n')
start = time()
dct = convert_instructions_to_dict(instructions,tenk_mapping_dict)
print("convert to dict time:", time()-start)
# save the dictionary to a JSON file
with open('dict.json', 'w', encoding='utf-8') as f:
    json.dump(dct, f, ensure_ascii=False, indent=4)

# save collapsed dict to a JSON file
collapsed_dct = collapse_dict(dct)
with open('collapsed_dict.json', 'w', encoding='utf-8') as f:
    json.dump(collapsed_dct, f, ensure_ascii=False, indent=4)