import re

def construct_dict(lines):
    # Track formatting styles in order of appearance
    format_priority = {}
    priority_counter = 0
    
    # apply rules
    
    # Process only non-table lines or isolated table rows (no table rows before/after)
    for i, line in enumerate(lines):
        # Skip empty lines
        if not line:
            continue
            
        # Check if this is a table line
        is_table_line = line[0]['in_table'] if line else False
        
        # Check if previous line is a table line
        prev_is_table = False
        if i > 0 and lines[i-1]:
            prev_is_table = lines[i-1][0]['in_table']
            
        # Check if next line is a table line
        next_is_table = False
        if i < len(lines) - 1 and lines[i+1]:
            next_is_table = lines[i+1][0]['in_table']
        
        # For isolated table rows, remove the in_table flag
        if is_table_line and not (prev_is_table or next_is_table):
            for item in line:
                item['in_table'] = False
                
        # Only combine items if not in a table OR it's an isolated table row (now marked as not in_table)
        if not is_table_line or (is_table_line and not (prev_is_table or next_is_table)):
            combined_items = []
            current_item = None
            
            for item in line:
                # Track format combinations in order of appearance
                format_combo = (
                    item['bold'], 
                    item['italic'], 
                    item['underline'], 
                    item.get('all_caps', False)
                )
                if format_combo not in format_priority:
                    format_priority[format_combo] = priority_counter
                    priority_counter += 1
                    
                if current_item is None:
                    current_item = item.copy()
                elif (current_item['bold'] == item['bold'] and 
                      current_item['italic'] == item['italic'] and
                      current_item['underline'] == item['underline'] and
                      current_item['height'] == item['height'] and
                      current_item['font_size'] == item['font_size'] and
                      current_item['in_table'] == item['in_table']):
                    # Combine with previous item if attributes match, adding space
                    current_item['text'] += ' ' + item['text']
                    # Replace double spaces with single spaces
                    while '  ' in current_item['text']:
                        current_item['text'] = current_item['text'].replace('  ', ' ')
                else:
                    # Add current_item to results and start a new one
                    combined_items.append(current_item)
                    current_item = item.copy()
            
            # Don't forget to add the last item
            if current_item is not None:
                combined_items.append(current_item)
            
            # Replace original line with combined items
            line[:] = combined_items

    # NEW CODE: Merge adjacent lines with same attributes
    i = 0
    while i < len(lines) - 1:
        # Skip empty lines
        if not lines[i] or not lines[i+1]:
            i += 1
            continue
            
        # Skip table lines
        if lines[i][0]['in_table'] or lines[i+1][0]['in_table']:
            i += 1
            continue
            
        # Get last item of current line and first item of next line
        last_item = lines[i][-1]
        first_item = lines[i+1][0]
        
        # Check if attributes match
        if (last_item['bold'] == first_item['bold'] and 
            last_item['italic'] == first_item['italic'] and
            last_item['underline'] == first_item['underline'] and
            last_item['height'] == first_item['height'] and
            last_item['font_size'] == first_item['font_size'] and
            last_item['in_table'] == first_item['in_table'] and
            last_item.get('indent', 0) == first_item.get('indent', 0)):  # Added check for matching indent
            
            # Merge the text
            last_item['text'] += ' ' + first_item['text']
            # Replace double spaces with single spaces
            while '  ' in last_item['text']:
                last_item['text'] = last_item['text'].replace('  ', ' ')
                
            # Remove the first item from the next line
            lines[i+1].pop(0)
            
            # If next line is now empty, remove it
            if not lines[i+1]:
                lines.pop(i+1)
                # Don't increment i since we removed a line
            # Otherwise, check again if the next item can be merged
            # (don't increment i)
        else:
            # Items don't match, move to next line
            i += 1

    # table handling - only process actual table lines (not the isolated ones we converted)
    for line in lines:
        # Skip if line is empty or not in a table
        if not line or not line[0]['in_table']:
            continue
            
        i = 0
        while i < len(line):
            item = line[i]
            
            # Check if item is just '$'
            if item['text'].strip() == '$':
                # If this is not the last item in the line
                if i < len(line) - 1:
                    # Move '$' to the beginning of the next cell's text
                    next_item = line[i+1]
                    next_item['text'] = '$' + next_item['text']
                    
                    # Remove the current item
                    line.pop(i)
                    # Don't increment i because we removed an item
                    # and the next item shifted to the current position
                else:
                    # If it's the last item, just keep it and move on
                    i += 1
            else:
                # Regular item, move to the next one
                i += 1

    # pruning - e.g. remove specific values like 'table of contents'
    for line in lines:
        if len(line) == 1:  
            item = line[0]
            text = item['text'].strip().lower()

            if text == 'table of contents':
                lines.remove(line)
                
            if re.match(r'^F?-?\d+$',text):
                lines.remove(line)
    
    # Helper function to count the number of True values in a formatting tuple
    def count_format_attributes(format_tuple):
        return sum(1 for attr in format_tuple if attr)
    
    # Helper function to check if an item is center-aligned
    def is_center_aligned(item):
        indent_value = item.get('indent', 0) or 0
        return 49.5 <= indent_value <= 50.5  # Allow slight variance around 50
    
    # Create result dictionary
    result = {'document': {}}
    
    # Initialize stack with root node
    # Format: (node, font_size, format_tuple, format_order, is_center_aligned, indent, level)
    stack = [(result['document'], 0, (False, False, False, False), 0, False, 999, 0)]
    
    # Add level and leveldesc to root document
    result['document']['level'] = 0
    result['document']['leveldesc'] = "Root document"
    
    for line in lines:
        if not line:
            continue
            
        if len(line) == 1:
            # This is a key
            item = line[0]
            key_text = item['text']
            
            # Extract all needed attributes
            font_size = item['font_size']
            format_tuple = (
                item['bold'], 
                item['italic'], 
                item['underline'], 
                item.get('all_caps', False)
            )
            format_count = count_format_attributes(format_tuple)
            center_aligned = is_center_aligned(item)
            indent_value = item.get('indent', 0) or 0
            
            # Get format order (which format combo appeared first)
            format_order = format_priority.get(format_tuple, 999)  # Default high if not found
            
            # Find the appropriate parent node using logical flow
            level_reason = []  # Track reasons for level assignment
            while len(stack) > 1:
                parent = stack[-1]
                parent_font_size = parent[1]
                parent_format_tuple = parent[2]
                parent_format_order = parent[3]
                parent_is_center = parent[4]
                parent_indent = parent[5]
                
                # Count parent's formatting attributes
                parent_format_count = count_format_attributes(parent_format_tuple)
                
                # 1. FONT SIZE CHECK - Most important
                if parent_font_size > font_size:
                    # Parent has larger font size - valid parent
                    level_reason.append(f"font size smaller than parent ({font_size} < {parent_font_size})")
                    break
                elif parent_font_size < font_size:
                    # Parent has smaller font size - invalid parent
                    level_reason.append(f"font size larger than parent ({font_size} > {parent_font_size})")
                    stack.pop()
                    continue
                
                # 2. FORMATTING COUNT CHECK - Compare number of formatting attributes
                if parent_format_count > format_count:
                    # Parent has more formatting attributes - valid parent
                    level_reason.append(f"fewer format attributes than parent ({format_count} < {parent_format_count})")
                    break
                elif parent_format_count < format_count:
                    # Parent has fewer formatting attributes - invalid parent
                    level_reason.append(f"more format attributes than parent ({format_count} > {parent_format_count})")
                    stack.pop()
                    continue
                
                # 3. FORMATTING TYPES CHECK - If same count, check if plain vs formatted
                # Plain text (no formatting) should never parent formatted text
                parent_has_formatting = parent_format_count > 0
                current_has_formatting = format_count > 0
                
                if current_has_formatting and not parent_has_formatting:
                    # Current has formatting but parent doesn't - invalid parent
                    level_reason.append("has formatting while parent doesn't")
                    stack.pop()
                    continue
                elif parent_has_formatting and not current_has_formatting:
                    # Parent has formatting but current doesn't - valid parent
                    level_reason.append("no formatting while parent has formatting")
                    break
                
                # 4. CENTER ALIGNMENT CHECK
                if parent_is_center and not center_aligned:
                    # Parent is center-aligned but current isn't - valid parent
                    level_reason.append("not center-aligned while parent is")
                    break
                elif not parent_is_center and center_aligned:
                    # Parent isn't center-aligned but current is - invalid parent
                    level_reason.append("center-aligned while parent isn't")
                    stack.pop()
                    continue
                
                # 5. INDENTATION CHECK - Only consider indentation if at least one has formatting
                # If both have no formatting, ignore indentation differences
                if parent_has_formatting or current_has_formatting:
                    if parent_indent < indent_value:
                        # Parent has less indentation - valid parent
                        level_reason.append(f"more indented than parent ({indent_value} > {parent_indent})")
                        break
                    elif parent_indent > indent_value:
                        # Parent has more indentation - invalid parent
                        level_reason.append(f"less indented than parent ({indent_value} < {parent_indent})")
                        stack.pop()
                        continue
                
                # 6. FORMAT ORDER CHECK - Final tiebreaker
                if parent_format_order < format_order:
                    # Parent format appeared earlier - valid parent
                    level_reason.append(f"format appeared later than parent ({format_order} > {parent_format_order})")
                    break
                
                # If we get here, all checks have failed - pop the stack
                level_reason.append("all hierarchy checks failed")
                stack.pop()
            
            # Get the parent node and its level
            parent_node = stack[-1][0]
            parent_level = stack[-1][6]
            
            # Create new node level (parent level + 1)
            new_level = parent_level + 1
            
            # Format description string for the level
            format_desc = []
            if format_tuple[0]:  # bold
                format_desc.append("bold")
            if format_tuple[1]:  # italic
                format_desc.append("italic")
            if format_tuple[2]:  # underline
                format_desc.append("underlined")
            if format_tuple[3]:  # all caps
                format_desc.append("ALL CAPS")
            
            format_str = " ".join(format_desc)
            if format_str:
                format_str = f"[{format_str}]"
            
            # Create the level description
            if level_reason:
                leveldesc = f"Level {new_level} due to: {'; '.join(level_reason)} {format_str}"
            else:
                leveldesc = f"Level {new_level} {format_str}"
            
            # Add this key to the parent
            parent_node[key_text] = {'level': new_level, 'leveldesc': leveldesc}
            
            # Push this node onto the stack
            stack.append((
                parent_node[key_text], 
                font_size, 
                format_tuple,
                format_order,
                center_aligned,
                indent_value,
                new_level
            ))
        else:
            # This is content
            content_text = ' '.join([item['text'] for item in line])
            
            # Add to the current node
            current_node = stack[-1][0]
            if 'text' in current_node:
                current_node['text'] += ' ' + content_text
            else:
                current_node['text'] = content_text

    return result