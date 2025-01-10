# Core functionality (original)
def standardize_css(style):
    if not style: 
        return {}
    return {
        k.strip(): v.strip().split() 
        for k, v in (pair.split(':') for pair in style.split(';') if ':' in pair)
        if k.strip() and v.strip()
    }

def get_node_styles(node):
    style = node.attributes.get('style')
    if not style:
        return {}
    return standardize_css(style)

def get_text_style(node, styles, inherited_style=None):
    text_style = inherited_style.copy() if inherited_style else {
        'bold': False,
        'italic': False,
        'underline': False
    }
    
    # Check HTML tags
    if node.tag in {'b', 'strong'}:
        text_style['bold'] = True
    if node.tag in {'i', 'em'}:
        text_style['italic'] = True
    if node.tag == 'u':
        text_style['underline'] = True
        
    # Check CSS styles
    font_weight = styles.get('font-weight', [''])[0]
    if font_weight in {'bold', '700', '800', '900'}:
        text_style['bold'] = True
        
    font_style = styles.get('font-style', [''])[0]
    if font_style == 'italic':
        text_style['italic'] = True
        
    text_decoration = styles.get('text-decoration', [''])[0]
    if 'underline' in text_decoration:
        text_style['underline'] = True
        
    return text_style

def get_indent(styles):
    margin_left = styles.get('margin-left', ['0'])[0]
    text_indent = styles.get('text-indent', ['0'])[0]
    
    try:
        margin = float(margin_left.rstrip('%')) if '%' in margin_left else float(margin_left)
    except ValueError:
        margin = 0
        
    try:
        indent = float(text_indent.rstrip('%')) if '%' in text_indent else float(text_indent)
    except ValueError:
        indent = 0
        
    return margin + indent

def is_inline(node, styles):
    if node.tag in {'span', 'a', 'strong', 'em', 'b', 'i', 'u'}:
        return True
    display = styles.get('display', [''])[0]
    return display == 'inline'

def iterwalk(root, include_text):
    def walk(node, inherited_styles=None, inherited_text_style=None):
        current_styles = dict(inherited_styles or {})
        node_styles = get_node_styles(node)
        current_styles.update(node_styles)
        
        if current_styles.get('display', [''])[0] == 'none':
            return
            
        text_content = node.text_content
        if text_content:
            text_transform = current_styles.get('text-transform', [''])[0]
            if text_transform == 'uppercase':
                text_content = text_content.upper()
            elif text_transform == 'lowercase':
                text_content = text_content.lower()
            elif text_transform == 'capitalize':
                text_content = text_content.capitalize()

        text_style = get_text_style(node, current_styles, inherited_text_style)
        
        yield ("start", node, current_styles, text_content, text_style)
        for child in node.iter(include_text=include_text):
            if child is not node:
                yield from walk(child, current_styles, text_style)
        yield ("end", node, current_styles, text_content, text_style)
    
    for node in root.iter(include_text=include_text):
        if node is not root:
            yield from walk(node)

# New height calculation functionality (add/modify these sections)
def parse_font_size(size_str, base_size):
    """Parse font size with precise point-to-pixel conversion"""
    try:
        if size_str.endswith('pt'):
            # Convert points to pixels (1pt = 1.333px)
            return float(size_str[:-2]) * 1.333
        elif size_str.endswith('px'):
            return float(size_str[:-2])
        elif size_str.endswith('%'):
            return base_size * float(size_str[:-1]) / 100
        elif size_str.endswith('em'):
            return base_size * float(size_str[:-2])
        elif size_str.endswith('rem'):
            return 16 * float(size_str[:-3])  # rem is relative to root (usually 16px)
        return float(size_str)  # Assume pixels if no unit
    except ValueError:
        return base_size  # Return base size if parsing fails

def get_effective_style(node, parent_styles=None):
    """Get combined styles considering element and parent context"""
    styles = {}
    
    # Start with parent styles
    if parent_styles:
        styles.update(parent_styles)
    
    # Add element's own styles
    element_styles = get_node_styles(node)
    for key, value in element_styles.items():
        if key in {'font-size', 'line-height', 'margin-top', 'margin-bottom',
                  'padding-top', 'padding-bottom', 'border-top', 'border-bottom'}:
            styles[key] = value
            
    return styles

def calculate_compound_height(node, inherited_size=None):
    """Calculate exact height based on all style factors"""
    base_size = inherited_size or 16
    styles = get_effective_style(node)
    
    # Get font size
    if 'font-size' in styles:
        font_size = parse_font_size(styles['font-size'][0], base_size)
    else:
        font_size = base_size
        
    # Calculate line height (default 1.2 if not specified)
    line_height_mult = 1.2
    if 'line-height' in styles:
        try:
            line_height_mult = float(styles['line-height'][0])
        except ValueError:
            pass
            
    content_height = font_size * line_height_mult
    
    # Add margins, padding, borders
    spacing = 0
    for prop in ['margin-top', 'margin-bottom', 'padding-top', 'padding-bottom']:
        if prop in styles:
            spacing += parse_font_size(styles[prop][0], base_size)
            
    # Handle borders
    if 'border-top' in styles:
        border_value = styles['border-top'][0].split()[0]
        spacing += parse_font_size(border_value, base_size)
    if 'border-bottom' in styles:
        border_value = styles['border-bottom'][0].split()[0]
        spacing += parse_font_size(border_value, base_size)

    # round to 2 decimal places
    font_size = round(font_size, 2)
    content_height = round(content_height, 2)
    spacing = round(spacing, 2)
        
    return {
        'font_size': font_size,
        'content_height': content_height,
        'total_height': content_height + spacing
    }

def html_reduction(tree):
    """Main processing function"""
    blocks = {'p', 'div', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'article', 'section', 'li'}
    skip_elements = {'script', 'style', 'noscript'}
    lines = []
    current_line = []
    row_content = []
    in_row = False
    inherited_size = 16  # Base font size
    
    def flush_line():
        if current_line:
            items = []
            for text, style in current_line:
                if text.strip():
                    height_metrics = calculate_compound_height(current_node, inherited_size)
                    items.append({
                        "text": text.strip(),
                        "indent": get_indent(current_styles),
                        "bold": style.get('bold', False),
                        "italic": style.get('italic', False),
                        "underline": style.get('underline', False),
                        "height": height_metrics['total_height'],
                        "font_size": height_metrics['font_size']
                    })
            if items:
                lines.append(items)
            current_line.clear()

    for event, node, styles, text_content, text_style in iterwalk(tree.body, include_text=True):
        if node.tag in skip_elements:
            continue

        current_node = node
        current_styles = styles
        current_text_style = text_style
        
        if event == "start":
            # Update inherited size based on parent styles
            if 'font-size' in styles:
                inherited_size = parse_font_size(styles['font-size'][0], inherited_size)

        # Process content based on node type
        if node.tag == 'tr':
            if event == "start":
                in_row = True
                row_content = []
            elif event == "end":
                if row_content:
                    height_metrics = calculate_compound_height(node, inherited_size)
                    lines.append([{
                        "text": text,
                        "indent": 0,
                        "bold": style['bold'],  # Use captured style
                        "italic": style['italic'],  # Use captured style
                        "underline": style['underline'],  # Use captured style
                        "height": height_metrics['total_height'],
                        "font_size": height_metrics['font_size']
                    } for text, style in row_content])  # Unpack both text and style
                in_row = False
                row_content = []
                continue

        if in_row and event == "start" and text_content:
            text = text_content.strip()
            if text:
                # Store both text and style
                row_content.append((text, text_style))
            continue
            
        if (node.tag in blocks or styles.get('display', [''])[0] == 'flex') and not is_inline(node, styles):
            if event == "start":
                flush_line()
                if text_content:
                    text = text_content.strip()
                    if text:
                        height_metrics = calculate_compound_height(node, inherited_size)
                        lines.append([{
                            "text": text,
                            "indent": get_indent(styles),
                            "bold": text_style['bold'],
                            "italic": text_style['italic'],
                            "underline": text_style['underline'],
                            "height": height_metrics['total_height'],
                            "font_size": height_metrics['font_size']
                        }])
            elif event == "end":
                flush_line()
        elif event == "start" and text_content:
            text = text_content.strip()
            if text:
                current_line.append((text, text_style))  # Store tuple of (text, style)
    
    flush_line()
    return lines