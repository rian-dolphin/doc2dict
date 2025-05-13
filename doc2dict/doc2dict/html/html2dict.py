from .instructions import convert_html_to_instructions
from selectolax.parser import HTMLParser
def html2dict(content,mapping_dict=None):
    parser = HTMLParser(content)
    body = parser.body
    instructions = convert_html_to_instructions(body, mapping_dict)