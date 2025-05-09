# we will introduce rules here later

# not sure where this should go yet
def clean_table(table_lines):
    pass

def merge_line(line):
    if len(line) <= 1:
        return line    
    
    if 'table' in line[0]:
        indices_to_remove = []
        for idx, _ in enumerate(line):
            if idx == len(line) - 2:
                break
            if ('cell' in line[idx] and 'cell' in line[idx + 1]):
                # check next item to see if cell is the same
                if line[idx]['cell'] == line[idx + 1]['cell']:
                    # merge the two items
                    line[idx]['text'] += line[idx + 1]['text']
                    indices_to_remove.append(idx + 1)

        # remove indices
        line = [item for idx, item in enumerate(line) if idx not in indices_to_remove]
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
    
# rewrite in to discrete.py
def strip_fake_tables(lines):
    for idx in range(len(lines)):
        if len(lines[idx]) <= 1:
            continue
            
        current_has_table = any('table' in item and item['table'] for item in lines[idx])
        if not current_has_table:
            continue
            
        prev_has_table = False
        if idx > 0:
            prev_has_table = any('table' in item and item['table'] for item in lines[idx-1])
            
        next_has_table = False
        if idx < len(lines) - 1:
            next_has_table = any('table' in item and item['table'] for item in lines[idx+1])
            
        if current_has_table and not prev_has_table and not next_has_table:
            # add is_table_header to every item with table key
            lines[idx] = [{**item, 'is_table_header': True} if 'table' in item and item['table'] else item for item in lines[idx]]
            # remove the table key from the current line
            lines[idx] = [{k: v for k, v in item.items() if k != 'table'} for item in lines[idx]]
            

            
    return lines

def clean_discrete(lines):
    lines = strip_fake_tables(lines)
    for idx,line in enumerate(lines):
            lines[idx] = merge_line(line)
    
    return lines
