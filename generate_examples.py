from selectolax.parser import HTMLParser
from doc2dict.doc2dict.html.convert_html_to_instructions import convert_html_to_instructions
from doc2dict.doc2dict.html.visualize_instructions import visualize_instructions
from doc2dict.doc2dict.html.visualize_dict import visualize_dict
from doc2dict.doc2dict.html.convert_instructions_to_dict import convert_instructions_to_dict, determine_levels
from doc2dict.doc2dict.html.mapping import dict_10k_html
from doc2dict.doc2dict.utils import unnest_dict, get_title
from time import time
import webbrowser
import json


# Benchmark bottom 150ms

file_path=r"C:\Users\jgfri\OneDrive\Desktop\doc2dict\a10-k20179302017.htm"
 

start = time()
with open(file_path, 'r', encoding='utf-8') as f:
    parser = HTMLParser(f.read())

print("load time:", time()-start)

start = time()
body = parser.body
instructions = convert_html_to_instructions(body)
print("convert to instructions time:", time()-start)

with open('instructions.txt', 'w', encoding='utf-8') as f:
    for instruction in instructions:
        f.write(str(instruction) + '\n')

# webbrowser.open(file_path)
#visualize_instructions(instructions)
levels = determine_levels(instructions, dict_10k_html)
with open('levels.txt', 'w', encoding='utf-8') as f:
    for level in levels:
        f.write(str(level) + '\n')
start = time()
dct = convert_instructions_to_dict(instructions,dict_10k_html)
print("convert to dict time:", time()-start)
# save the dictionary to a JSON file
with open('dict.json', 'w', encoding='utf-8') as f:
    json.dump(dct, f, ensure_ascii=False, indent=4)


#visualize_dict(dct)
with open('unnest.txt', 'w',encoding='utf-8') as f:
    f.write(unnest_dict(dct['document'][1357]))

print(get_title(dct, r'strat.*'))