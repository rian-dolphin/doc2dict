
from collections import defaultdict

def clean_table(data):
    # Group text by row and cell
    cells = defaultdict(lambda: defaultdict(str))
    
    for item in data:
        if 'row' in item and 'cell' in item:
            # Get text from either 'text' or 'text:center' key
            text = item.get('text', '')
            cells[item['row']][item['cell']] += text
    
    # Build table as nested lists with proper sorting
    table = []
    for row_id in sorted(cells.keys(), key=lambda x: int(x) if x.isdigit() else x):
        row = []
        for cell_id in sorted(cells[row_id].keys(), key=lambda x: int(x) if x.isdigit() else x):
            row.append(cells[row_id][cell_id].strip())
        table.append(row)
    
    return table



def merge_line(line):
    if len(line) <= 1:
        return line
    
    if 'table' in line[0]:
        line = clean_table(line)
        return [{'cleaned_table': line}]
                
        
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
    

def clean_fake_tables(lines):
            
    return lines

def clean_discrete(lines):
    #lines = clean_fake_tables(lines)

    indices_to_remove = []
    for idx,line in enumerate(lines):
            cleaned_line=merge_line(line)
            lines[idx] = cleaned_line
    lines = [item for idx, item in enumerate(lines) if idx not in indices_to_remove]
    return lines