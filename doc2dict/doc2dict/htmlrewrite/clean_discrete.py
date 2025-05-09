# we will introduce rules here later

# change to not unique.
def merge_line(line):
    if len(line) <= 1:
        return line
    

        
    
    if 'table' in line[0]:
        if any(['cell' in item for item in line]):
            combined_text = ''.join(d['text'] for d in line)
            new_dict = line[0].copy()
            new_dict['text'] = combined_text
            return [new_dict]
        else:
            return line
        
    # Find the first non-empty item to use as reference
    non_empty_items = [item for item in line if item['text'].strip() != '']
    if not non_empty_items:
        return line
        
    reference_item = non_empty_items[0]
    
    # Check if all non-empty items have the same formatting attributes
    if all(all(item.get(attr) == reference_item.get(attr) for attr in ['bold', 'italic', 'underline']) 
           for item in non_empty_items):
        combined_text = ''.join(d['text'] for d in line)
        # Create a new copy based on the reference item
        new_dict = reference_item.copy()
        new_dict['text'] = combined_text
        return [new_dict]
    else:
        return line

def clean_discrete(lines):
    for idx,line in enumerate(lines):
            lines[idx] = merge_line(line)
    
    return lines
