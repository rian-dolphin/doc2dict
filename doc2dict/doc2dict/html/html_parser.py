import re
from selectolax.parser import HTMLParser

def extract_indent(style_str):
    """
    Extract indentation from a style string using regex
    Returns the indent value as a percentage of screen width or 50% for centered text
    """
    # Check for center alignment first
    if re.search(r'text-align:\s*center', style_str) or re.search(r'margin:\s*auto', style_str):
        return 50.0  # 50% indicates centered text
    
    # Extract margin-left value
    margin_left = 0
    margin_match = re.search(r'margin-left:([^;]+)', style_str)
    if margin_match:
        margin_value = margin_match.group(1).strip()
        # Handle percentage, px, em, etc.
        if '%' in margin_value:
            # Already a percentage, use directly
            try:
                margin_left = float(margin_value.replace('%', ''))
            except ValueError:
                pass
        elif 'px' in margin_value:
            # Convert pixels to percentage (assuming 1000px as reference width)
            try:
                px_value = float(margin_value.replace('px', ''))
                margin_left = (px_value / 1000) * 100
            except ValueError:
                pass
        elif 'em' in margin_value:
            # Convert em to percentage (assuming 1em = 16px and 1000px width)
            try:
                em_value = float(margin_value.replace('em', ''))
                px_value = em_value * 16
                margin_left = (px_value / 1000) * 100
            except ValueError:
                pass
    
    # Extract text-indent value (same conversion logic)
    text_indent = 0
    indent_match = re.search(r'text-indent:([^;]+)', style_str)
    if indent_match:
        indent_value = indent_match.group(1).strip()
        # Same percentage conversion as above
        if '%' in indent_value:
            try:
                text_indent = float(indent_value.replace('%', ''))
            except ValueError:
                pass
        elif 'px' in indent_value:
            try:
                px_value = float(indent_value.replace('px', ''))
                text_indent = (px_value / 1000) * 100
            except ValueError:
                pass
        elif 'em' in indent_value:
            try:
                em_value = float(indent_value.replace('em', ''))
                px_value = em_value * 16
                text_indent = (px_value / 1000) * 100
            except ValueError:
                pass
    
    # Total indent is the sum (now as percentage)
    return margin_left + text_indent
def extract_font_size(style_str):
    """
    Extract the font size from a style string
    Returns the font size in pixels (converted if necessary)
    """
    size_match = re.search(r'font-size:([^;]+)', style_str)
    if size_match:
        size_value = size_match.group(1).strip()
        # Handle various units
        if 'pt' in size_value:
            try:
                pt_value = float(size_value.replace('pt', ''))
                return pt_value * 1.333  # 1pt ≈ 1.333px
            except ValueError:
                pass
        elif 'px' in size_value:
            try:
                return float(size_value.replace('px', ''))
            except ValueError:
                pass
        elif 'em' in size_value:
            try:
                em_value = float(size_value.replace('em', ''))
                return em_value * 16  # 1em = 16px as standard
            except ValueError:
                pass
        elif '%' in size_value:
            try:
                percent = float(size_value.replace('%', ''))
                return percent * 0.16  # 100% = 16px
            except ValueError:
                pass
    
    # Default font size if not specified
    return 16.0  # Standard browser default

def is_in_table(node):
    """Check if a node is inside a table"""
    current = node
    while current:
        if current.tag == 'table' or current.tag == 'tr' or current.tag == 'td' or current.tag == 'th':
            return True
        current = current.parent
    return False

def html_reduction(tree):
    """Extract text with formatting and indentation from HTML"""
    lines = []
    current_line = []
    in_table = False
    
    # Process all paragraph and block elements
    for node in tree.css('p, div, h1, h2, h3, h4, h5, h6, li, tr, td, th'):
        # Skip empty nodes
        if not node.text():
            continue
        
        # Check if we're in a table
        if node.tag in ['table', 'tr', 'td', 'th'] or is_in_table(node):
            in_table = True
        else:
            in_table = False
        
        # Get style attributes
        style_str = node.attributes.get('style', '')
        
        # Get indent
        indent = extract_indent(style_str)
        
        # Get font size
        font_size = extract_font_size(style_str)
        
        # Process each text node or formatted span
        items = []
        for child in node.iter():
            if child.tag == 'span' or child is node:
                text = child.text()
                if not text or not text.strip():
                    continue
                
                # Get child style
                child_style = child.attributes.get('style', '')
                
                # Determine formatting
                bold = ('font-weight:bold' in child_style or 
                        'font-weight: bold' in child_style or
                        'font-weight:700' in child_style or
                        child.tag == 'b' or 
                        child.tag == 'strong')
                
                italic = ('font-style:italic' in child_style or 
                         'font-style: italic' in child_style or
                         child.tag == 'i' or 
                         child.tag == 'em')
                
                underline = ('text-decoration:underline' in child_style or
                            'text-decoration: underline' in child_style or
                            child.tag == 'u')
                
                # Check if text is all caps (for text with more than 1 character)
                text_strip = text.strip()
                all_caps = text_strip.isupper() and len(text_strip) > 1
                
                # Create item dictionary
                items.append({
                    "text": text_strip,
                    "bold": bold,
                    "italic": italic,
                    "underline": underline,
                    "all_caps": all_caps,  # New property
                    "height": font_size * 1.2,  # Approximate total height
                    "font_size": font_size,
                    "in_table": in_table,
                    "indent": indent
                })
        
        if items:
            lines.append(items)
    
    return lines

def html2dict(content):
    """Process HTML content into a structured format with indentation"""
    # Parse HTML
    html = HTMLParser(content)
    lines = html_reduction(html)
    
    # Process individual lines to combine adjacent items with the same attributes
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
                      current_item['all_caps'] == item.get('all_caps', False) and  # Add all_caps comparison
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

    # Merge adjacent lines with same attributes
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
            last_item['all_caps'] == first_item.get('all_caps', False) and  # Add all_caps comparison
            last_item['height'] == first_item['height'] and
            last_item['font_size'] == first_item['font_size'] and
            last_item['in_table'] == first_item['in_table']):
            
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

    # Table handling - only process actual table lines (not the isolated ones we converted)
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

    # Convert to hierarchical dictionary
    # Helper function to determine priority of text attributes
    def get_priority(item):
        # Base priority from formatting attributes
        if item['bold'] and item['italic'] and item['underline']:
            priority = 7  # highest priority
        elif item['bold'] and item['italic']:
            priority = 6
        elif item['bold'] and item['underline']:
            priority = 5
        elif item['bold']:
            priority = 4
        elif item['italic'] and item['underline']:
            priority = 3
        elif item['italic']:
            priority = 2
        elif item['underline']:
            priority = 1
        else:
            priority = 0  # plain text, lowest priority
        
        # Add a small boost for all caps text
        if item.get('all_caps', False):
            priority += 0.5
            
        return priority
    
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