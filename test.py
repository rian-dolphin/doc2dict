from selectolax.parser import HTMLParser
from time import time

# What we need to keep track of
# bold
# italic
# underline
# all caps
# table

# indent (and 50% indent from center align)

# font size

# we will likely highly modify this 
def get_font_size(style_dict):
    if 'font-size' in style_dict:
        return style_dict['font-size']


def walk(node):
    yield ("start",node)
    for child in node.iter(include_text=True):
        yield from walk(child)

    yield ("end",node)

def check_text_style(text):
    # Check if the text is all caps
    if text.isupper():
        return True
    return False

def get_indent(style_dict):
    if 'text-align' in style_dict:
        if style_dict['text-align'] == 'center':
            return 50
        
    # need to normalize the way user sees it
    # need to do weird stuff for negative margins
    


def style_to_dict(style_string):
    style_list = [attr.strip() for attr in style_string.split(';') if attr.strip()]
    result = {}
    for item in style_list:
        if ':' in item:
            key, value = item.split(':', 1)
            result[key.strip()] = value.strip()
    return result

def get_style(node):
    attributes = {}
    style = node.attributes.get('style', '')
    style_dict = style_to_dict(style)
    if 'font-weight' in style_dict:
        if style_dict['font-weight'] == 'bold':
            attributes['bold'] = True
        elif style_dict['font-weight'] == '700':
            attributes['bold'] = True

    if 'font-style' in style_dict:
        if style_dict['font-style'] == 'italic':
            attributes['italic'] = True
    
    if 'text-decoration' in style_dict:
        if style_dict['text-decoration'] == 'underline':
            attributes['underline'] = True

    get_indent(style_dict)
    return attributes


def reduce_html(root):
    attribute_dict = {'bold': 0, 'italic': 0, 'underline': 0, 'table': 0}
    for signal,node in walk(root):
        if signal == "start":
            # do style check here
            style_attributes = get_style(node)
            for key in style_attributes:
                if key in attribute_dict:
                    attribute_dict[key] += 1

            # do tag check here
            if node.tag in ['b','strong']:
                attribute_dict['bold'] += 1
            elif node.tag in ['i','em']:
                attribute_dict['italic'] += 1
            elif node.tag in ['u','ins']:
                attribute_dict['underline'] += 1
            elif node.tag in ['table']:
                attribute_dict['table'] += 1
            elif node.tag == '-text':
                # check for all caps
                text = node.text_content
                if check_text_style(text):
                    attribute_dict['all_caps'] = 1
                else:
                    attribute_dict['all_caps'] = 0
                #print(attribute_dict | {'text': node.text_content})


        elif signal == "end":
            # do style check here
            style_attributes = get_style(node)
            for key in style_attributes:
                if key in attribute_dict:
                    attribute_dict[key] = max(attribute_dict[key] - 1,0)

            if node.tag in ['p', 'div', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'li', 'tr', 'td', 'th']:
                # do something
                pass

            

            elif node.tag in ['b','strong']:
                attribute_dict['bold'] = max(attribute_dict['bold'] - 1,0)
            elif node.tag in ['i','em']:
                attribute_dict['italic'] = max(attribute_dict['italic'] - 1,0)
            elif node.tag in ['u','ins']:
                attribute_dict['underline'] = max(attribute_dict['underline'] - 1,0)
            elif node.tag in ['table']:
                attribute_dict['table'] = max(attribute_dict['table'] - 1,0)
                
        

# Benchmark bottom 150ms
start = time()

file_path=r'C:\Users\jgfri\OneDrive\Desktop\test\test\0000320193-24-000123\aapl-20240928.htm'
with open(file_path, 'r', encoding='utf-8') as f:
    parser = HTMLParser(f.read())

print(f"Time taken to parse HTML:", time() - start)

root = parser.root

reduce_time = time()
reduce_html(root)
print("Time taken to reduce HTML:", time() - reduce_time)
