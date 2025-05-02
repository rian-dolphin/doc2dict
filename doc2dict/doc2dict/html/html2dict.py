from .html_parser import html_reduction
from selectolax.parser import HTMLParser

def html2dict(content):
    html = HTMLParser(content)
    lines = html_reduction(html)
    
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

    # Helper function to determine priority of text attributes
    def get_priority(item):
        # For text formatting attributes with all possible combinations
        attr_priority = 0
        all_caps = item.get('all_caps', False)
        
        # All combinations with bold, italic, underline, all_caps
        if item['bold'] and item['italic'] and item['underline'] and all_caps:
            attr_priority = 15  # highest priority
        elif item['bold'] and item['italic'] and item['underline']:
            attr_priority = 14
        elif item['bold'] and item['italic'] and all_caps:
            attr_priority = 13
        elif item['bold'] and item['italic']:
            attr_priority = 12
        elif item['bold'] and item['underline'] and all_caps:
            attr_priority = 11
        elif item['bold'] and item['underline']:
            attr_priority = 10
        elif item['bold'] and all_caps:
            attr_priority = 9
        elif item['bold']:
            attr_priority = 8
        elif item['italic'] and item['underline'] and all_caps:
            attr_priority = 7
        elif item['italic'] and item['underline']:
            attr_priority = 6
        elif item['italic'] and all_caps:
            attr_priority = 5
        elif item['italic']:
            attr_priority = 4
        elif item['underline'] and all_caps:
            attr_priority = 3
        elif item['underline']:
            attr_priority = 2
        elif all_caps:
            attr_priority = 1
        else:
            attr_priority = 0  # plain text, lowest priority
        
        # Create a single priority value
        # Formula gives highest weight to font size,
        # medium weight to indentation (inverted so less indent = higher priority)
        # and lowest weight to text attributes
        
        indent_value = item.get('indent', 0) or 0
        
        # Scale factors to ensure proper hierarchy
        # font_size * 1000 ensures it's the primary factor
        # (100 - indent_value/10) ensures less indented items have higher priority
        # attr_priority is now on a 0-15 scale
        
        return (item['font_size'] * 1000) + (100 - min(indent_value/10, 99)) + (attr_priority * 0.1)
    
    # Create result dictionary
    result = {'document': {}}
    
    # Initialize stack with root node
    stack = [(result['document'], 0, -1)]  # (node, font_size, priority)
    
    for line in lines:
        if not line:
            continue
            
        if len(line) == 1:
            # This is a key
            item = line[0]
            key_text = item['text']
            font_size = item['font_size']
            priority = get_priority(item)
            
            # Find the appropriate parent node
            while len(stack) > 1:
                parent_font_size = stack[-1][1]
                parent_priority = stack[-1][2]
                
                # If parent has larger font size or same font size with higher priority, it's a valid parent
                if parent_font_size > font_size or (parent_font_size == font_size and parent_priority > priority):
                    break
                    
                # Otherwise, pop the stack
                stack.pop()
            
            # Get the parent node
            parent_node = stack[-1][0]
            
            # Add this key to the parent
            parent_node[key_text] = {}
            
            # Push this node onto the stack
            stack.append((parent_node[key_text], font_size, priority))
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