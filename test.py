from selectolax.parser import HTMLParser
from doc2dict.doc2dict.htmlrewrite.flow import convert_html_to_flow
from doc2dict.doc2dict.htmlrewrite.discrete import convert_instructions_to_discrete
            
        

# Benchmark bottom 150ms

file_path=r'C:\Users\jgfri\OneDrive\Desktop\test\test\0000320193-24-000123\aapl-20240928.htm'
with open(file_path, 'r', encoding='utf-8') as f:
    parser = HTMLParser(f.read())

body = parser.body
instructions = convert_html_to_flow(body)

with open('instructions.txt', 'w', encoding='utf-8') as f:
    for instruction in instructions:
        f.write(str(instruction) + '\n')

lines = convert_instructions_to_discrete(instructions)
with open('discrete.txt', 'w', encoding='utf-8') as f:
    for line in lines:
        f.write(str(line) + '\n')



