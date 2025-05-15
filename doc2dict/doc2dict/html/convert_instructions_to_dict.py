import re
import pkg_resources

version = pkg_resources.get_distribution("doc2dict").version

tenk_mapping_dict = {
    ('part',r'^part\s*([ivx]+)$','part') : 0,
    ('signatures',r'^signatures?\.*$','signatures') : 0,
    ('item',r'^item\s*(\d+)','item') : 1,
}


def determine_levels(instructions_list, mapping_dict):
    # first we want to identify out the text

    # filter out tables
    headers = [instructions[0] if 'text' in instructions[0] else {} for instructions in instructions_list]
    likely_header_attributes = ['bold','italic','underline','text-center']
    # identify likely text nodes, return {} if not
    headers = [item if any([item.get(attr, False) for attr in likely_header_attributes]) else {} for item in headers]
    # count font-size
    font_size_counts = {size: sum(1 for item in [instr[0] for instr in instructions_list if 'text' in instr[0]] if item.get('font-size') == size) for size in set(item.get('font-size') for item in [instr[0] for instr in instructions_list if 'text' in instr[0]] if item.get('font-size') is not None)}
    most_common_font_size, font_count = max(font_size_counts.items(), key=lambda x: x[1])
    if font_count > (.5 * len(instructions_list)):
        # assume anything with less than this font size is subscript
        headers = [item if item.get('font-size') is None or item.get('font-size') >= most_common_font_size else {} for item in headers]


    levels = []
    for header in headers:
        level = None
        if 'text' in header:
            text = header['text'].lower()
            regex_tuples = [(item[0][1], item[0][0], item[1],item[0][2]) for item in mapping_dict.items()]
            for regex, header, hierarchy_level, header_class in regex_tuples:
                if re.match(regex, text):
                    # Found a section header
                    level = (hierarchy_level,header_class)
                    break
        if level is None:
            levels.append((-1,'textclass'))
        else:
            levels.append(level)
    return levels

# prob here we want to find the attributes first (fast)
# then try for the regex.
def convert_instructions_to_dict(instructions_list, mapping_dict):
    # Get pre-calculated levels for each instruction
    levels = determine_levels(instructions_list, mapping_dict)
    
    # Initialize document structure
    document = {'contents': {}}
    
    # Create an introduction section
    introduction = {'title': 'introduction', 'class': 'introduction', 'contents': {}}
    
    # Add the introduction to the document
    document['contents'][-1] = introduction
    
    # Keep track of current position in hierarchy
    current_section = introduction
    current_path = [document, introduction]  # Path from root to current section
    current_levels = [-1, 0]  # Corresponding hierarchy levels
    
    # Process each instruction using pre-calculated levels
    for idx, instructions in enumerate(instructions_list):
        instruction = instructions[0]
        level,header_class = levels[idx]
        
        if level >= 0:
            # This is a section header
            
            # Pop hierarchy until finding appropriate parent
            while len(current_levels) > 1 and current_levels[-1] >= level:
                current_path.pop()
                current_levels.pop()
            
            # Extract title and determine class from the instruction
            title = instruction['text']
            
            # Create new section
            new_section = {'title': title, 'class': header_class, 'contents': {}}
            
            # Add section to parent's contents with index as key
            parent = current_path[-1]
            parent['contents'][idx] = new_section
            
            # Update tracking
            current_path.append(new_section)
            current_levels.append(level)
            current_section = new_section
        else:
            # Regular content - add to current section
            current_section['contents'][idx] = instruction
    
    # Create final result with metadata
    result = {
        'metadata': {
            'parser': 'doc2dict',
            'github': 'https://github.com/john-friedman/doc2dict',
            'version': version
        },
        'document': document['contents']
    }
    
    return result

