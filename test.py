from selectolax.parser import HTMLParser
from doc2dict.doc2dict.htmlrewrite.flow import convert_html_to_flow
from doc2dict.doc2dict.htmlrewrite.discrete import convert_instructions_to_discrete
from doc2dict.doc2dict.htmlrewrite.visualize_discrete import visualize_discrete
from time import time

# Benchmark bottom 150ms

start = time()
file_path=r'C:\Users\jgfri\OneDrive\Desktop\test\test\0000320193-24-000123\aapl-20240928.htm'
with open(file_path, 'r', encoding='utf-8') as f:
    parser = HTMLParser(f.read())

print("load time:", time()-start)

start = time()
body = parser.body
instructions = convert_html_to_flow(body)
print("convert to instructions time:", time()-start)

with open('instructions.txt', 'w', encoding='utf-8') as f:
    for instruction in instructions:
        f.write(str(instruction) + '\n')

start = time()
lines = convert_instructions_to_discrete(instructions)
print("convert to discrete time:", time()-start)
with open('discrete.txt', 'w', encoding='utf-8') as f:
    for line in lines:
        f.write(str(line) + '\n')


visualize_discrete(lines)
