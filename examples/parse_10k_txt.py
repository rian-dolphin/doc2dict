from doc2dict import txt2dict
from doc2dict.txt.mapping_dicts import dict_10k
import json
from time import time
# Load and process 10-K
with open('../samples/10-k_toc_item_cont.txt', 'r') as f:
    content = f.read()
    
lines = content.split('\n')
s = time()
result = txt2dict(content, dict_10k)

# Save result to JSON
with open('10k.json', 'w', encoding='utf-8') as f:
    json.dump(result, f, indent=4)