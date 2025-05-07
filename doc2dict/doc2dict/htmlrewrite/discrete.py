



def convert_instructions_to_discrete(instructions):
    current_line = []
    lines = []

    attributes = {'bold':0, 'italic':0, 'underline':0, 'all_caps':0,'text:center':0,'font-size':[]}

    bool_attributes = ['bold', 'italic', 'underline', 'all_caps', 'text:center']
    
    for instruction in instructions:
        if not instruction:
            lines.append(current_line)
            current_line = []
        
        if 'text' in instruction:
            current_dict_attributes = {}
            for bool_attribute in bool_attributes:
                if attributes[bool_attribute] > 0:
                    current_dict_attributes[bool_attribute] = True
            current_line.append(current_dict_attributes| {'text': instruction['text']})

        if 'start' in instruction:
            for bool_attribute in bool_attributes:
                if bool_attribute in instruction['start']:
                    attributes[bool_attribute] += 1

        elif 'end' in instruction:
            for bool_attribute in bool_attributes:
                if bool_attribute in instruction['end']:
                    attributes[bool_attribute] -= 1

    return lines