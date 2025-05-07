

# What we need to keep track of
# bold
# italic
# underline
# all caps
# table
# font size

# indent (and 50% indent from center align)


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
    
    # probably should normalize this.
    if 'font-size' in style_dict:
        font_size = style_dict['font-size']
        attributes[f"font-size:{font_size}"] = True


    if 'text-align' in style_dict:
        if style_dict['text-align'] == 'center':
            attributes['text:center'] = True
    
    if 'display' in style_dict:
        if style_dict['display'] == 'none':
            attributes['display:none'] = True
        
    return attributes


def convert_html_to_flow(root):
    attributes_list = []
    skip_invisible = False
    for signal,node in walk(root):
        if signal == "start":
            # skip invisible elements
            if skip_invisible:
                continue

            # do style check here
            style_attributes = get_style(node)
            if 'display:none' in style_attributes:
                skip_invisible = True
                continue
            for key in style_attributes:
                if style_attributes[key]:
                    attributes_list.append({'start': key})

            # do tag check here
            if node.tag in ['b','strong']:
                attributes_list.append({'start': 'bold'})
            elif node.tag in ['i','em']:
                attributes_list.append({'start': 'italic'})
            elif node.tag in ['u','ins']:
                attributes_list.append({'start': 'underline'})
            elif node.tag in ['table']:
                attributes_list.append({'start': 'table'})
            elif node.tag == '-text':
                # check for all caps
                text = node.text_content
                if check_text_style(text):
                    attributes_list.append({'start': 'all_caps'})
                    attributes_list.append({'text': text})
                    attributes_list.append({'end': 'all_caps'})
                else:
                    attributes_list.append({'text': text})


        elif signal == "end":
            # do style check here
            style_attributes = get_style(node)
            if 'display:none' in style_attributes:
                skip_invisible = False
                continue
            for key in style_attributes:
                if style_attributes[key]:
                    attributes_list.append({'end': key})

            if node.tag in ['p', 'div', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'li', 'tr', 'td', 'th']:
                attributes_list.append({})

            elif node.tag in ['b','strong']:
                attributes_list.append({'end': 'bold'})
            elif node.tag in ['i','em']:
                attributes_list.append({'end': 'italic'})
            elif node.tag in ['u','ins']:
                attributes_list.append({'end': 'underline'})
            elif node.tag in ['table']:
                attributes_list.append({'end': 'table'})
    
    return attributes_list