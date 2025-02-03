from doc2dict.mapping import DocumentProcessor
from doc2dict.txt.mapping_dicts import dict_10k
import json
from time import time
# Load and process 10-K
with open('../samples/10-k_toc.txt', 'r') as f:
    content = f.read()
    
lines = content.split('\n')
s = time()
processor = DocumentProcessor(dict_10k)
print(f"Init time: {time()-s}")
result = processor.process(lines)

# Save result to JSON
with open('10k.json', 'w', encoding='utf-8') as f:
    json.dump(result, f, indent=4)