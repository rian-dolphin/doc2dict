
# we can dramatically improve output here using same location of cells.
#hmm. we should make cell count go to zero every new table.
def clean_table(line):

    remove_modifiers = ['$',',']
    left_modifiers = ['(']
    right_modifiers = [')']
    
    # merge cells
    cells = []
    current_cell = None
    for item in line:
        if 'cell' in item:
            item_cell = item['cell']
            if current_cell is None:
                current_cell = item_cell
                cells.append(item)
            elif current_cell == item_cell:
                # merge the two items
                cells[-1]['text'] += item['text']
            else:
                current_cell = item_cell
                cells.append(item)

    # remove empty strings
    cells = [cell for cell in cells if cell['text'].strip() != '']

    # modifiers
    indices_to_remove = []
    for idx in range(len(cells)):
        if cells[idx]['text'].strip() in remove_modifiers:
            indices_to_remove.append(idx)
            continue
        if (cells[idx]['text'].strip() in left_modifiers and idx < len(cells) - 1):
            indices_to_remove.append(idx)
            cells[idx + 1]['text'] = cells[idx]['text'] + cells[idx + 1]['text']
            continue
        if (cells[idx]['text'].strip() in right_modifiers and idx > 0):
            indices_to_remove.append(idx)
            cells[idx - 1]['text'] = cells[idx - 1]['text'] + cells[idx]['text']
            continue


    cells = [cells[idx] for idx in range(len(cells)) if idx not in indices_to_remove]
    text_list = [cell['text'] for cell in cells]

    return text_list

def merge_line(line):
    if len(line) <= 1:
        return line, ""
    
    if 'table' in line[0]:
        line = clean_table(line)
        return line, "table"
                
        
    # Find the first non-empty item to use as reference
    non_empty_items = [item for item in line if item['text'].strip() != '']
    if not non_empty_items:
        return line, ""
        
    reference_item = non_empty_items[0]
    
    # Check if all non-empty items have the same formatting attributes
    if all(all(item.get(attr) == reference_item.get(attr) for attr in ['bold', 'italic', 'underline']) 
           for item in non_empty_items):
        combined_text = ''.join(d['text'] for d in line)
        # Create a new copy based on the reference item
        new_dict = reference_item.copy()
        new_dict['text'] = combined_text
        return [new_dict], ""
    else:
        return line, ""
    

def clean_fake_tables(lines):
            
    return lines

def clean_discrete(lines):
    #lines = clean_fake_tables(lines)

    in_table = False
    table = []
    indices_to_remove = []
    for idx,line in enumerate(lines):
            cleaned_line, command = merge_line(line)
            # check if we at end of lines and in a table
            if ((command == "table") & (idx == len(lines) - 1)):
                if len(cleaned_line) > 0:
                    table.append(cleaned_line)
                lines[idx] = [{'cleaned_table': table}]
                table = []
                in_table = False
            elif command == "table":
                if len(cleaned_line) > 0:
                    table.append(cleaned_line)
                indices_to_remove.append(idx)
                in_table = True
            else:
                if in_table:
                    in_table = False
                    lines[idx] = [{'cleaned_table': table}]
                    table = []
                else:
                    lines[idx] = cleaned_line
    lines = [item for idx, item in enumerate(lines) if idx not in indices_to_remove]
    return lines
