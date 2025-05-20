def get_font_attributes(dct):
    if 'font_name' in dct:
        attribute = dct['font_name'].split('-')
        if len(attribute) > 1:
            key = attribute[-1].lower()
            dct[key] = True
    return dct

def get_font_size(coords_tuple):
    left = coords_tuple[0]
    bottom = coords_tuple[1]
    right = coords_tuple[2]
    top = coords_tuple[3]
    height = top - bottom
    font_size = height / 2
    return font_size

def assign_line(instructions_stream):
    """
    Assign line numbers to text elements that are positioned on the same line.
    Only compares with the next neighbor in the list.
    """
    
    # Initialize with first element
    current_line = 0
    instructions_list = []
    instructions = [instructions_stream[0]]
    
    # Process remaining elements
    for i in range(len(instructions_stream) - 1):
        current = instructions_stream[i]
        next_item = instructions_stream[i + 1]
        
        # Extract y-coordinates (bottom of text)
        current_y = current['coords'][1]  # bottom y of current
        next_y = next_item['coords'][1]   # bottom y of next
        
        # Get font sizes for tolerance calculation
        current_font_size = current['font_size']
        next_font_size = next_item['font_size']
        
        # Calculate tolerance based on larger font size
        tolerance = max(current_font_size, next_font_size) * 0.5
        
        # Check if next item is on the same line
        if abs(current_y - next_y) <= tolerance:
            instructions.append(next_item)
        else:
            instructions_list.append(instructions)
            instructions = [next_item]
    
    return instructions_list

# so these need to be modified to look at all the dicts.
def get_left_indent(coords_tuple):
    return

def get_is_centered(coords_tuple):
    return