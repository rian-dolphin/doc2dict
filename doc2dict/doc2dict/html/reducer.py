import re
from selectolax.parser import HTMLParser

# Style extraction modules
def parse_style_string(style_str):
    """Parse style string into a dictionary"""
    if not style_str or style_str is None:
        return {}
    
    styles = {}
    for rule in style_str.split(';'):
        if ':' in rule:
            prop, value = rule.split(':', 1)
            styles[prop.strip()] = value.strip()
    
    return styles

def check_visibility(styles):
    """Check if element is visible based on styles"""
    if styles.get('display') == 'none':
        return False
    if styles.get('visibility') == 'hidden':
        return False
    return True

def get_text_formatting(node, styles):
    """Extract text formatting information (bold, italic, underline)"""
    formatting = {
        'bold': False,
        'italic': False,
        'underline': False
    }
    
    # Check style attribute
    font_weight = styles.get('font-weight', '')
    if font_weight in ['bold', '700']:
        formatting['bold'] = True
    
    font_style = styles.get('font-style', '')
    if font_style == 'italic':
        formatting['italic'] = True
    
    text_decoration = styles.get('text-decoration', '')
    if 'underline' in text_decoration:
        formatting['underline'] = True
    
    # Check tag names
    if node.tag in ['b', 'strong']:
        formatting['bold'] = True
    if node.tag in ['i', 'em']:
        formatting['italic'] = True
    if node.tag == 'u':
        formatting['underline'] = True
    
    return formatting

def extract_font_size(styles):
    """Extract the font size from styles dictionary"""
    font_size = styles.get('font-size', '')
    
    if not font_size:
        return 16.0  # Default
    
    # Handle various units
    if 'pt' in font_size:
        try:
            pt_value = float(font_size.replace('pt', ''))
            return pt_value * 1.333  # 1pt ≈ 1.333px
        except ValueError:
            pass
    elif 'px' in font_size:
        try:
            return float(font_size.replace('px', ''))
        except ValueError:
            pass
    elif 'em' in font_size:
        try:
            em_value = float(font_size.replace('em', ''))
            return em_value * 16  # 1em = 16px as standard
        except ValueError:
            pass
    elif '%' in font_size:
        try:
            percent = float(font_size.replace('%', ''))
            return percent * 0.16  # 100% = 16px
        except ValueError:
            pass
    
    return 16.0  # Default

def extract_indent(styles):
    """Extract indentation from styles dictionary"""
    # Check for center alignment first
    text_align = styles.get('text-align', '')
    margin = styles.get('margin', '')
    
    if text_align == 'center' or margin == 'auto':
        return 50.0  # 50% indicates centered text
    
    margin_left = parse_css_unit(styles.get('margin-left', '0'))
    text_indent = parse_css_unit(styles.get('text-indent', '0'))
    
    return margin_left + text_indent

def parse_css_unit(value):
    """Parse CSS unit and convert to percentage"""
    if not value or value == '0':
        return 0
    
    if '%' in value:
        try:
            return float(value.replace('%', ''))
        except ValueError:
            return 0
    elif 'px' in value:
        try:
            px_value = float(value.replace('px', ''))
            return (px_value / 1000) * 100  # assuming 1000px reference width
        except ValueError:
            return 0
    elif 'em' in value:
        try:
            em_value = float(value.replace('em', ''))
            px_value = em_value * 16
            return (px_value / 1000) * 100
        except ValueError:
            return 0
    
    return 0

def is_block_element(node):
    """Check if node is a block-level element"""
    block_tags = ['p', 'div', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'li', 'tr', 'td', 'th']
    return node.tag in block_tags

def is_table_element(node):
    """Check if node is a table-related element"""
    table_tags = ['table', 'tr', 'td', 'th']
    return node.tag in table_tags

def check_all_caps(text):
    """Check if text is all caps (more than 1 character)"""
    text_strip = text.strip()
    return text_strip.isupper() and len(text_strip) > 1

# Main iteration function
def iterwalk(root):
    """Walk the DOM tree with style inheritance"""
    def walk(node, inherited_styles=None, in_table=False):
        # Get node's own styles
        style_str = node.attributes.get('style', '')
        node_styles = parse_style_string(style_str)
        
        # Merge with inherited styles
        current_styles = dict(inherited_styles or {})
        current_styles.update(node_styles)
        
        # Check visibility
        if not check_visibility(current_styles):
            return
        
        # Update table context
        if is_table_element(node):
            in_table = True
        
        yield ("start", node, current_styles, in_table)
        
        # Walk children
        for child in node.iter():
            if child is not node:
                yield from walk(child, current_styles, in_table)
        
        yield ("end", node, current_styles, in_table)
    
    yield from walk(root)

def html_reduction(content):
    """Extract text with formatting and indentation from HTML"""
    tree = HTMLParser(content)
    lines = []
    
    # Process all block elements
    for block in tree.css('p, div, h1, h2, h3, h4, h5, h6, li, tr, td, th'):
        # Skip if element is hidden
        style_str = block.attributes.get('style', '')
        block_styles = parse_style_string(style_str)
        if not check_visibility(block_styles):
            continue
        
        # Get block properties
        in_table = is_table_element(block) or any(p.tag in ['table', 'tr', 'td', 'th'] for p in [block.parent] if p)
        
        # Create a list to hold all text items in this block
        block_items = []
        
        # Keep track of which text has been processed
        processed_text = set()
        
        # Process text directly in the block (not in spans)
        direct_text = ""
        for node in block.iter(include_text=True):
            # Only get text nodes that are direct children of the block
            if node.parent is block and not hasattr(node, 'tag'):
                if node.text_content:
                    direct_text += node.text_content + " "
        
        direct_text = direct_text.strip()
        if direct_text:
            formatting = get_text_formatting(block, block_styles)
            font_size = extract_font_size(block_styles)
            indent = extract_indent(block_styles)
            
            block_items.append({
                "text": direct_text,
                "bold": formatting['bold'],
                "italic": formatting['italic'],
                "underline": formatting['underline'],
                "all_caps": check_all_caps(direct_text),
                "height": font_size * 1.2,
                "font_size": font_size,
                "in_table": in_table,
                "indent": indent
            })
            processed_text.add(direct_text)
        
        # Process all spans within this block
        for span in block.css('span, b, i, u, strong, em'):
            # Get span styles
            span_style_str = span.attributes.get('style', '')
            span_styles = parse_style_string(span_style_str)
            
            # Merge with block styles
            merged_styles = dict(block_styles)
            merged_styles.update(span_styles)
            
            # Check visibility
            if not check_visibility(merged_styles):
                continue
            
            # Get text content
            text = span.text()
            if not text or not text.strip():
                continue
                
            # Skip if we've already processed this exact text
            text = text.strip()
            if text in processed_text:
                continue
                
            # Get formatting
            formatting = get_text_formatting(span, merged_styles)
            font_size = extract_font_size(merged_styles)
            indent = extract_indent(merged_styles)
            
            block_items.append({
                "text": text,
                "bold": formatting['bold'],
                "italic": formatting['italic'],
                "underline": formatting['underline'],
                "all_caps": check_all_caps(text),
                "height": font_size * 1.2,
                "font_size": font_size,
                "in_table": in_table,
                "indent": indent
            })
            processed_text.add(text)
        
        if block_items:
            lines.append(block_items)
    
    return lines