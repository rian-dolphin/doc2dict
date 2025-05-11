
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


def convert_instructions_to_discrete(instructions):
    current_line = []
    lines = []

    attributes = {'bold':0, 'italic':0, 'underline':0, 'all_caps':0,'text:center':0,'font-size':[],
                  'left-indent':0}

    bool_attributes = ['bold', 'italic', 'underline', 'all_caps', 'text:center']

    cell = None
    table = None
    row = None
    
    for instruction in instructions:
        if not instruction:
            if current_line:
                lines.append(current_line)
            current_line = []
            continue
        
        if 'text' in instruction:
            current_dict_attributes = {}
            for bool_attribute in bool_attributes:
                if attributes[bool_attribute] > 0:
                    current_dict_attributes[bool_attribute] = True
            
            font_size = None
            if len(attributes['font-size']) > 0:
                font_size = attributes['font-size'][-1]

            dct = {}
            if cell is not None:
                dct['cell'] = cell.split(':')[1]
            if row is not None:
                dct['row'] = row.split(':')[1]
            if table is not None:
                dct['table'] = table.split(':')[1]

            current_line.append(dct | current_dict_attributes| {'text': instruction['text'], 'font-size': font_size, 'left-indent': attributes['left-indent']})

        #note that instruvtions only have one thing, so we should end after a match.
        # todo later
        if 'start' in instruction:
            for bool_attribute in bool_attributes:
                if bool_attribute in instruction['start']:
                    attributes[bool_attribute] += 1
            
            if 'font-size' in instruction['start']:
                font_size = instruction['start'].split(':')[1]
                attributes['font-size'].append(font_size)

            # Handle left indent (padding-left, margin-left, text-indent)
            for indent_prop in ['padding-left', 'margin-left', 'text-indent']:
                if indent_prop in instruction['start']:
                    indent_value = instruction['start'].split(':')[1]
                    
                    # Get current font context for unit conversion
                    font_context = attributes['font-size'][-1] if attributes['font-size'] else None
                    
                    # Convert to pixels and add to total
                    px_value = normalize_to_px(indent_value, font_context)
                    attributes['left-indent'] += px_value
                    break  # Process only one property if multiple are specified

            if 'cell' in instruction['start']:
                if cell is None:
                    cell = instruction['start']
            elif 'row' in instruction['start']:
                if row is None:
                    row = instruction['start']
            elif 'table' in instruction['start']:
                if table is None:
                    table = instruction['start']


            

        elif 'end' in instruction:
            for bool_attribute in bool_attributes:
                if bool_attribute in instruction['end']:
                    attributes[bool_attribute] -= 1

            if 'font-size' in instruction['end']:
                if attributes['font-size']:  # Check if there's anything to pop
                    attributes['font-size'].pop()

            # Handle left indent removal (padding-left, margin-left, text-indent)
            for indent_prop in ['padding-left', 'margin-left', 'text-indent']:
                if indent_prop in instruction['end']:
                    indent_value = instruction['end'].split(':')[1]
                    
                    # Get current font context for unit conversion
                    font_context = attributes['font-size'][-1] if attributes['font-size'] else None
                    
                    # Convert to pixels and subtract from total
                    px_value = normalize_to_px(indent_value, font_context)
                    attributes['left-indent'] -= px_value
                    break  # Process only one property if multiple are specified

            if 'cell' in instruction['end']:
                if cell == instruction['end']:
                    cell = None
            elif 'row' in instruction['end']:
                if row == instruction['end']:
                    row = None
            elif 'table' in instruction['end']:
                if table == instruction['end']:
                    table = None

    # Add any remaining line
    if current_line:
        lines.append(current_line)
        
    return lines