# params 
tag_groups = {
"bold": ["b", "strong"],
"italic": ["i", "em"],
"underline": ["u", "ins"],
}

# utils
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
    increments = []
    stacks = []
    style = node.attributes.get('style', '')
    style_dict = style_to_dict(style)
    if 'font-weight' in style_dict:
        if style_dict['font-weight'] == 'bold':
            increments.append('bold')
        elif style_dict['font-weight'] == '700':
            increments.append('bold')

    if 'font-style' in style_dict:
        if style_dict['font-style'] == 'italic':
            increments.append('italic')
    
    if 'text-decoration' in style_dict:
        if style_dict['text-decoration'] == 'underline':
            increments.append('underline')    

    if 'text-align' in style_dict:
        if style_dict['text-align'] == 'center':
            increments.append('text-center')

    if 'font-size' in style_dict:
        font_size = style_dict['font-size']
        font_size = normalize_to_px(font_size)
        stacks.append({'font-size': font_size})
    
    if 'text-indent' in style_dict:
        indent = style_dict['text-indent']
        indent = normalize_to_px(indent)
        stacks.append({'left-indent': indent})

    if 'padding' in style_dict:
        padding_value = style_dict['padding']
        # Handle four-value format: top right bottom left
        if padding_value.count(' ') == 3:
            _, _, _, left = padding_value.split(' ')
            left = normalize_to_px(left)
            stacks.append({'padding-left': left})
        # Handle three-value format: top right/left bottom
        elif padding_value.count(' ') == 2:
            _, right_left, _ = padding_value.split(' ')
            right_left = normalize_to_px(right_left)
            stacks.append({'padding-left': right_left})
        # Handle two-value format: top/bottom right/left
        elif padding_value.count(' ') == 1:
            _, right_left = padding_value.split(' ')
            right_left = normalize_to_px(right_left)
            stacks.append({'padding-left': right_left})
        # Handle single-value format: all sides
        else:
            padding_value = normalize_to_px(padding_value)
            stacks.append({'padding-left': padding_value})

    # Also handle direct padding-left if specified
    if 'padding-left' in style_dict:
        padding_left = style_dict['padding-left']
        padding_left = normalize_to_px(padding_left)
        stacks.append({'padding-left': padding_left})

    # Handle margin with the same logic as padding
    if 'margin' in style_dict:
        margin_value = style_dict['margin']
        # Handle four-value format: top right bottom left
        if margin_value.count(' ') == 3:
            _, _, _, left = margin_value.split(' ')
            left = normalize_to_px(left)
            stacks.append({'margin-left': left})
        # Handle three-value format: top right/left bottom
        elif margin_value.count(' ') == 2:
            _, right_left, _ = margin_value.split(' ')
            right_left = normalize_to_px(right_left)
            stacks.append({'margin-left': right_left})
        # Handle two-value format: top/bottom right/left
        elif margin_value.count(' ') == 1:
            _, right_left = margin_value.split(' ')
            right_left = normalize_to_px(right_left)
            stacks.append({'margin-left': right_left})
        # Handle single-value format: all sides
        else:
            margin_value = normalize_to_px(margin_value)
            stacks.append({'margin-left': margin_value})

    # Handle direct margin-left if specified
    if 'margin-left' in style_dict:
        margin_left = style_dict['margin-left']
        margin_left = normalize_to_px(margin_left)
        stacks.append({'margin-left': margin_left})

    if 'display' in style_dict:
        if style_dict['display'] == 'none':
            increments.append('display-none')

        
    return increments, stacks

def parse_css_value(value_str):
    """Extract numeric value and unit from CSS value string"""
    if not value_str or not isinstance(value_str, str):
        return 0, 'px'
    
    value_str = value_str.strip()
    
    # Handle non-numeric values
    if value_str in ['auto', 'inherit', 'initial']:
        return 0, value_str
    
    # Find where the number ends
    numeric_part = ''
    for i, char in enumerate(value_str):
        if char.isdigit() or char == '.':
            numeric_part += char
        elif char == '-' and i == 0:  # Handle negative values
            numeric_part += char
        else:
            unit = value_str[i:].strip()
            break
    else:
        unit = 'px'  # Default if no unit specified
    
    # Convert numeric part to float
    try:
        value = float(numeric_part) if numeric_part else 0
    except ValueError:
        value = 0
    
    return value, unit


def normalize_to_px(value_str, font_context=None):
    """Convert any CSS measurement to pixels based on context"""
    if not value_str:
        return 0
    
    # Parse the value
    value, unit = parse_css_value(value_str)
    
    # Early return for non-numeric values
    if unit in ['auto', 'inherit', 'initial']:
        return 0
    
    # Get font context in pixels
    current_font_size = 16  # Default
    if font_context:
        font_value, font_unit = parse_css_value(font_context)
        if font_unit == 'px':
            current_font_size = font_value
        elif font_unit == 'pt':
            current_font_size = font_value * 1.333
        else:
            # For simplicity, treat all other units as approximately 16px
            current_font_size = font_value * 16 if font_value else 16
    
    # Convert to pixels
    if unit == 'px':
        return value
    elif unit == 'pt':
        return value * 1.333
    elif unit == 'em':
        return value * current_font_size
    elif unit == 'rem':
        return value * 16  # Root em always based on root font size
    elif unit == '%':
        return value * current_font_size / 100  # % of font size
    elif unit == 'ex':
        return value * current_font_size / 2  # Roughly half the font size
    elif unit == 'ch':
        return value * current_font_size * 0.5  # Approximate character width
    elif unit in ['vh', 'vw', 'vmin', 'vmax']:
        return value  # Cannot accurately convert viewport units without screen size
    elif unit == 'cm':
        return value * 37.8  # Approximate for screen (96dpi)
    elif unit == 'mm':
        return value * 3.78  # 1/10th of cm
    elif unit == 'in':
        return value * 96  # Standard 96dpi
    elif unit == 'pc':
        return value * 16  # 1pc = 12pt
    else:
        return value  # Unknown unit, return as is

def safe_increment(dct,key):
    if key not in dct:
        dct[key] = 0

    dct[key] += 1

def safe_decrement(dct,key):
    if key not in dct:
        dct[key] = 0

    dct[key] -= 1
    if dct[key] < 0:
        dct[key] = 0

def safe_stack(dct,key,val):
    if key not in dct:
        dct[key] = []

    dct[key].append(val)

def safe_unstack(dct,key):
    if key not in dct:
        dct[key] = []

    if len(dct[key]) > 0:
        dct[key].pop()
    else:
        dct[key] = []

def parse_start_style(current_attributes,node):
    increments, stacks = get_style(node)
    if 'display-none' in increments:
        return 'skip'

    for key in increments:
        safe_increment(current_attributes,key)

    for stack in stacks:
        for key in stack:
            safe_stack(current_attributes,key,stack[key])

    return ''
def parse_end_style(current_attributes,node):
    increments,stacks = get_style(node)
    if 'display-none' in increments:
        return 'skip'
    
    for key in increments:
        safe_decrement(current_attributes,key)

    for stack in stacks:
        for key in stack:
            safe_unstack(current_attributes,key)

    return ''

def parse_start_tag(current_attributes,node):
    tag = node.tag

    if tag == 'table':
        return 'table'
    elif tag == 'tr':
        return ''
    elif tag in ['td', 'th']:
        return ''
    elif tag == '-text':
        return 'text'

    for tag in tag_groups:
        if node.tag in tag_groups[tag]:
            safe_increment(current_attributes,tag)
            return ''
        
def parse_end_tag(current_attributes,node):
    tag = node.tag

    if tag == 'table':
        return 'table'
    elif tag == 'tr':
        return ''
    elif tag in ['td', 'th']:
        return ''
    elif tag in ['p', 'div', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'li','br']:
        return 'newline'

    for tag in tag_groups:
        if node.tag in tag_groups[tag]:
            safe_decrement(current_attributes,tag)
            return ''

def convert_html_to_instructions(root):
    skip_node = False
    in_table = False

    instructions_list = []
    instructions = []
    current_attributes = {}


    for signal,node in walk(root):
        if signal == "start":
            # skip invisible elements
            if skip_node:
                continue
            elif in_table:
                continue
            
            style_command = parse_start_style(current_attributes,node)
            if style_command == 'skip':
                skip_node = True
                continue

            tag_command = parse_start_tag(current_attributes,node)
            if tag_command == 'table':
                in_table = True
                continue
            elif tag_command == 'text':
                text = node.text_content
                instruction = {'text': text}

                if check_text_style(text):
                    instruction['text-style'] = 'all_caps'

                for key in current_attributes:
                    val = current_attributes[key]
                    if isinstance(val, list):
                        if len(val) > 0:
                            instruction[key] = val[-1]
                    elif isinstance(val, int):
                        if val > 0:
                            instruction[key] = True

                instructions.append(instruction)


        elif signal == "end":
            
            style_command = parse_end_style(current_attributes,node)
            if style_command == 'skip':
                skip_node = False
                continue

            tag_command = parse_end_tag(current_attributes,node)
            if tag_command == 'table':
                in_table = False
                continue
            elif tag_command == 'newline':
                instructions_list.append(instructions)
                instructions = []

    # add any remaining instructions
    if instructions:
        instructions_list.append(instructions)
    return instructions_list