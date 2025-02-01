from doc2dict.mapping import DocumentProcessor
from doc2dict.txt.mapping_dicts import dict_10k
import json
# Load and process 10-K
with open('../samples/10-k.txt', 'r') as f:
    content = f.read()
    
lines = content.split('\n')
processor = DocumentProcessor(dict_10k)
result = processor.process(lines)

# Save result to JSON
with open('10k.json', 'w', encoding='utf-8') as f:
    json.dump(result, f, indent=4)