

def convert_instructions_to_discrete(instructions):
    current_line = []
    lines = []

    attributes = {'bold':0, 'italic':0, 'underline':0, 'all_caps':0,'text:center':0,'table':0,'font-size':[]}

    bool_attributes = ['bold', 'italic', 'underline', 'all_caps', 'text:center','table']
    
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
            
            if len(attributes['font-size']) > 0:
                font_size = attributes['font-size'][-1]
            current_line.append(current_dict_attributes| {'text': instruction['text'], 'font-size': font_size})

        if 'start' in instruction:
            for bool_attribute in bool_attributes:
                if bool_attribute in instruction['start']:
                    attributes[bool_attribute] += 1
            
            if 'font-size' in instruction['start']:
                font_size = instruction['start'].split(':')[1]
                attributes['font-size'].append(font_size)

        elif 'end' in instruction:
            for bool_attribute in bool_attributes:
                if bool_attribute in instruction['end']:
                    attributes[bool_attribute] -= 1

            if 'font-size' in instruction['end']:
                attributes['font-size'].pop()

    return lines