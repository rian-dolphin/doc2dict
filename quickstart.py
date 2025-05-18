from doc2dict.doc2dict.html.html2dict import html2dict
from time import time

# Load your html file
with open('apple_10k_2024.htm','r') as f:
    content = f.read()

# Parse 
s = time()
dct = html2dict(content,mapping_dict=None)
print("Parsing time:", time()-s)

# Visualize Parsing
#visualize_dict(dct)