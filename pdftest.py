
from doc2dict.doc2dict.html.convert_instructions_to_dict import convert_instructions_to_dict
pdf_path = r'msft_proxy.pdf'
from doc2dict.doc2dict.pdf.convert_pdf_to_instructions import convert_pdf_to_instructions
from doc2dict.doc2dict.html.visualize_dict import visualize_dict

with open(pdf_path, 'rb') as f:
    content = f.read()


instructions_list = convert_pdf_to_instructions(content)
with open('instructions_list.txt', 'w',encoding='utf-8') as f:
    for item in instructions_list:
        f.write(str(item) + '\n')
dct = convert_instructions_to_dict(instructions_list)
visualize_dict(dct)