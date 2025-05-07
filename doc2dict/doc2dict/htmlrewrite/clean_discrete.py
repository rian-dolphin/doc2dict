# we will introduce rules here later

# change to not unique.
def merge_line(line):
    if len(line) == 1:
        return line

    if all(all(item.get(attr) == line[0].get(attr) for attr in ['bold', 'italic', 'underline']) for item in line if item['text'].strip() !=  ''):
        combined_text = ''.join(d['text'] for d in line)
        # create a new copy of the first dict in the line
        # and set the text to the combined text
        new_dict = line[0].copy()
        new_dict['text'] = combined_text
        return [new_dict]
    else:
        return line

def clean_discrete(lines):
    for idx,line in enumerate(lines):
        if len(line) > 1:
            # merge if attributes are the same
            
            lines[idx] = merge_line(line)
    
    return lines