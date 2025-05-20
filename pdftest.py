

pdf_path = r'msft_proxy.pdf'
from doc2dict.doc2dict.pdf.convert_pdf_to_instructions import convert_pdf_to_instructions

with open(pdf_path, 'rb') as f:
    content = f.read()


instructions_list = convert_pdf_to_instructions(content)
for instruction in instructions_list:
    print(instruction)