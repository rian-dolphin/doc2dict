import re
import pkg_resources

version = pkg_resources.get_distribution("doc2dict").version

tenk_mapping_dict = {
    ('part',r'^part\s*([ivx]+)$') : 0,
    ('signatures',r'^signatures?\.*$') : 0,
    ('item',r'^item\s*(\d+)$') : 1,
}

def determine_hierarchy(instructions_list, mapping_dict):
    return mapping_dict

def convert_instructions_to_dict(instructions_list, mapping_dict):
    # Initialize with just base
    document = {'contents': {}}
    
    hierarchy_dict = determine_hierarchy(instructions_list, mapping_dict)
    
    # Create an introduction section
    introduction = {'title': 'introduction', 'class': 'introduction', 'contents': {}}
    
    # Add the introduction to the document with a specific index
    # Using 'intro' as the key to ensure it appears first
    document['contents'][-1] = introduction
    
    # Keep track of current position in hierarchy
    current_section = introduction  # Start with introduction as current section
    current_path = [document, introduction]  # Path now includes introduction
    current_levels = [-1, 0]  # Introduction is at level 0 like other top sections

    
    # Process each instruction
    for idx, instructions in enumerate(instructions_list):
        instruction = instructions[0]
        
        # Check if this is a potential section header
        if 'text' in instruction:
            text = instruction['text'].lower()
            
            # Try to match against regex patterns
            regex_tuples = [(item[0][1], item[0][0], item[1]) for item in hierarchy_dict.items()]
            for regex, header, hierarchy_level in regex_tuples:
                if re.match(regex, text):
                    # Found a section header
                    
                    # Pop path until we find appropriate parent level
                    while len(current_levels) > 1 and current_levels[-1] >= hierarchy_level:
                        current_path.pop()
                        current_levels.pop()
                    
                    # Create new section
                    new_section = {'title': text, 'class': header, 'contents': {}}
                    
                    # Add section to parent's contents
                    parent = current_path[-1]
                    parent['contents'][idx] = new_section
                    
                    # Update current path
                    current_path.append(new_section)
                    current_levels.append(hierarchy_level)
                    current_section = new_section
                    
                    break
            else:
                # Not a section header, add content to current section
                current_section['contents'][idx] = instruction
        else:
            # No text, add content to current section
            current_section['contents'][idx] = instruction
    
    # Add metadata
    result = {
        'metadata': {
            'parser': 'doc2dict',
            'github': 'https://github.com/john-friedman/doc2dict',
            'version': version
        },
        'document': document
    }
    
    return result