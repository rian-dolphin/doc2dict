pdf_path = r"d506673dars.pdf"
from doc2dict.doc2dict.pdf.convert_pdf_to_instructions import convert_pdf_to_instructions
from doc2dict.doc2dict.pdf.mapping import pdf_base_mapping_dict
from doc2dict.doc2dict.html.convert_instructions_to_dict import determine_levels, convert_instructions_to_dict
from doc2dict.doc2dict.html.visualize_dict import visualize_dict
from doc2dict.doc2dict.html.visualize_instructions import visualize_instructions 
from doc2dict.doc2dict import pdf2dict
import webbrowser as wb
from time import time 

with open(pdf_path, 'rb') as f:
    content = f.read()
start = time()
dct=pdf2dict(content)
print("load time:", time()-start)


#wb.open(pdf_path)
instructions = convert_pdf_to_instructions(content) 
visualize_instructions(instructions)
with open('example_output/pdf/pdf_instructions.txt', 'w', encoding='utf-8') as f:
    for instruction in instructions:
        f.write(str(instruction) + '\n')

levels = determine_levels(instructions, pdf_base_mapping_dict)
with open('example_output/pdf/pdf_levels.txt', 'w', encoding='utf-8') as f:
    for level in levels:
        f.write(str(level) + '\n')


dct = convert_instructions_to_dict(instructions, pdf_base_mapping_dict)


visualize_dict(dct)
import json
with open('example_output/pdf/pdf_dict.json', 'w', encoding='utf-8') as f:
    json.dump(dct, f, ensure_ascii=False, indent=4)