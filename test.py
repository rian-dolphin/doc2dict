from selectolax.parser import HTMLParser
from doc2dict.doc2dict.htmlrewrite2.instructions import convert_html_to_instructions

from time import time
import webbrowser

# Benchmark bottom 150ms

#file_path=r'C:\Users\jgfri\OneDrive\Desktop\test\test\0000320193-24-000123\aapl-20240928.htm'
file_path = r"C:\Users\jgfri\OneDrive\Desktop\test\test\0000950170-24-087843\msft-20240630.htm"


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
