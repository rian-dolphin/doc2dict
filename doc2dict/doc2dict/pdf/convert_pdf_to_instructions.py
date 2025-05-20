import pypdfium2 as pdfium
import pypdfium2.raw as pdfium_c
from ctypes import c_ushort, c_ulong, POINTER, c_float, c_void_p, c_size_t, c_uint8
from .pdf_utils import get_text, get_font_data, get_font
from .utils import get_font_attributes, get_left_indent, get_is_centered, get_font_size, assign_line


def convert_pdf_to_instructions(content):

    # Open the PDF
    pdf = pdfium.PdfDocument(content)

    instructions_stream = []
    # Extract text and font info from each page
    for page_index in range(len(pdf)):
        page = pdf[page_index]
        text_page = page.get_textpage()
        page_width = page.get_width()
        

        # Get page objects
        for obj in page.get_objects():
            text = get_text(text_page, obj)
            font = get_font(obj)
            font_raw_data = get_font_data(font)
            font_attributes = get_font_attributes(font_raw_data)
            
            

            # left bottom righ top
            coords_tuple = obj.get_pos()
            font_size = get_font_size(coords_tuple)

            instruction = {'text': text} | font_attributes | {'coords': coords_tuple,'font-size': font_size}
            instructions_stream.append(instruction)

    
    # Clean up resources
    pdf.close()

    instructions_list = assign_line(instructions_stream)

    # now we 
    return instructions_list