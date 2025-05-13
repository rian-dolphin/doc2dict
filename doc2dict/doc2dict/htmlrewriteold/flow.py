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
    
    if 'text-indent' in style_dict:
        indent = style_dict['text-indent']
        attributes[f"text-indent:{indent}"] = True

    if 'padding' in style_dict:
        padding_value = style_dict['padding']
        # Handle four-value format: top right bottom left
        if padding_value.count(' ') == 3:
            _, _, _, left = padding_value.split(' ')
            attributes[f"padding-left:{left}"] = True
        # Handle three-value format: top right/left bottom
        elif padding_value.count(' ') == 2:
            _, right_left, _ = padding_value.split(' ')
            attributes[f"padding-left:{right_left}"] = True
        # Handle two-value format: top/bottom right/left
        elif padding_value.count(' ') == 1:
            _, right_left = padding_value.split(' ')
            attributes[f"padding-left:{right_left}"] = True
        # Handle single-value format: all sides
        else:
            attributes[f"padding-left:{padding_value}"] = True

    # Also handle direct padding-left if specified
    if 'padding-left' in style_dict:
        padding_left = style_dict['padding-left']
        attributes[f"padding-left:{padding_left}"] = True

    # Handle margin with the same logic as padding
    if 'margin' in style_dict:
        margin_value = style_dict['margin']
        # Handle four-value format: top right bottom left
        if margin_value.count(' ') == 3:
            _, _, _, left = margin_value.split(' ')
            attributes[f"margin-left:{left}"] = True
        # Handle three-value format: top right/left bottom
        elif margin_value.count(' ') == 2:
            _, right_left, _ = margin_value.split(' ')
            attributes[f"margin-left:{right_left}"] = True
        # Handle two-value format: top/bottom right/left
        elif margin_value.count(' ') == 1:
            _, right_left = margin_value.split(' ')
            attributes[f"margin-left:{right_left}"] = True
        # Handle single-value format: all sides
        else:
            attributes[f"margin-left:{margin_value}"] = True

    # Handle direct margin-left if specified
    if 'margin-left' in style_dict:
        margin_left = style_dict['margin-left']
        attributes[f"margin-left:{margin_left}"] = True
    if 'display' in style_dict:
        if style_dict['display'] == 'none':
            attributes['display:none'] = True



        
    return attributes


def convert_html_to_flow(root):
    attributes_list = []
    skip_invisible = False
    in_table = False
    cell_id = 0
    row_id = 0
    table_id = 0
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
                attributes_list.append({})
                attributes_list.append({'start': f'table:{table_id}'})
                in_table = True
            elif node.tag == '-text':
                # check for all caps
                text = node.text_content
                if check_text_style(text):
                    attributes_list.append({'start': 'all_caps'})
                    attributes_list.append({'text': text})
                    attributes_list.append({'end': 'all_caps'})
                else:
                    attributes_list.append({'text': text})
            elif node.tag in ['td', 'th']:
                attributes_list.append({'start': f'cell:{cell_id}'})
                if node.attributes.get('colspan'):
                    colspan = node.attributes['colspan']
                    attributes_list.append({'start': f"colspan:{colspan}"})
            elif node.tag in ['tr']:
                attributes_list.append({'start': f'row:{row_id}'})
                row_id += 1
            


        elif signal == "end":
            # do style check here
            style_attributes = get_style(node)
            if 'display:none' in style_attributes:
                skip_invisible = False
                continue
            for key in style_attributes:
                if style_attributes[key]:
                    attributes_list.append({'end': key})

            if node.tag in ['p', 'div', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'li','br']:
                if not in_table:
                    attributes_list.append({})
            elif node.tag == 'tr':
                attributes_list.append({'end': f'row:{row_id-1}'})
                # reset cell id
                cell_id = 0
                    
            elif node.tag in ['b','strong']:
                attributes_list.append({'end': 'bold'})
            elif node.tag in ['i','em']:
                attributes_list.append({'end': 'italic'})
            elif node.tag in ['u','ins']:
                attributes_list.append({'end': 'underline'})
            elif node.tag in ['td', 'th']:
                attributes_list.append({'end': f'cell:{cell_id}'})
                cell_id += 1
                if node.attributes.get('colspan'):
                    colspan = node.attributes['colspan']
                    attributes_list.append({'end': f"colspan:{colspan}"})
            elif node.tag in ['table']:
                attributes_list.append({'end': f'table:{table_id}'})
                # reset row id
                row_id = 0
                table_id += 1
                attributes_list.append({})
                in_table = False
    
    return attributes_list