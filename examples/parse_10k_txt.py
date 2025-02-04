from datamule import Document
import json
from time import time
from pathlib import Path
document = Document(filename=Path('../samples/tsla10k.html'),type='10-K')
document.parse()

with open('tsla10k.json', 'w', encoding='utf-8') as f:
    json.dump(document.data, f, indent=4)  