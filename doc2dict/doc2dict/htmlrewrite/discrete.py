



def convert_instructions_to_discrete(instructions):
    current_line = []
    lines = []
    attributes = {}
    for instruction in instructions:
        if not instruction:
            lines.append(current_line)
            current_line = []
        
        if 'text' in instruction:
            current_line.append(attributes | {'text': instruction['text']})

    return lines