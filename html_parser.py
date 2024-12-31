from selectolax.parser import HTMLParser
from time import time
from visualizer import format_list_html

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

def get_text_style(node, styles):
    """Extract text styling from both tags and CSS"""
    # Initialize with default values
    text_style = {
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

def iterwalk(root, include_text):
    def walk(node, inherited_styles=None):
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

        text_style = get_text_style(node, current_styles)
        yield ("start", node, current_styles, text_content, text_style)
        for child in node.iter(include_text=include_text):
            if child is not node:
                yield from walk(child, current_styles)
        yield ("end", node, current_styles, text_content, text_style)
    
    for node in root.iter(include_text=include_text):
        if node is not root:
            yield from walk(node)

def is_inline(node, styles):
    if node.tag in {'span', 'a', 'strong', 'em', 'b', 'i', 'u'}:  # Added 'u'
        return True
    display = styles.get('display', [''])[0]
    return display == 'inline'

def html_reduction(tree):
    blocks = {'p', 'div', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'article', 'section', 'li'}
    skip_elements = {'script', 'style', 'noscript'}
    lines = []
    current_line = []
    row_content = []
    in_row = False
    current_indent = 0
    current_style = None
    
    def flush_line():
        if current_line:
            items = [
                {
                    "text": item.strip(), 
                    "indent": current_indent,
                    "bold": current_style.get('bold', False) if current_style else False,
                    "italic": current_style.get('italic', False) if current_style else False,
                    "underline": current_style.get('underline', False) if current_style else False
                } 
                for item in current_line if item.strip()
            ]
            if items:
                lines.append(items)
            current_line.clear()

    for event, node, styles, text_content, text_style in iterwalk(tree.body, include_text=True):
        if node.tag in skip_elements:
            continue

        is_flex = styles.get('display', [''])[0] == 'flex'
        
        if event == "start" and (node.tag in blocks or is_flex):
            current_indent = get_indent(styles)
            current_style = text_style

        # Handle table rows
        if node.tag == 'tr':
            if event == "start":
                in_row = True
                row_content = []
            elif event == "end":
                if row_content:
                    lines.append([{
                        "text": text, 
                        "indent": 0,
                        "bold": False,
                        "italic": False,
                        "underline": False
                    } for text in row_content])
                in_row = False
                row_content = []
                continue

        if in_row and event == "start" and text_content:
            text = text_content.strip()
            if text:
                row_content.append(text)
            continue
            
        if (node.tag in blocks or is_flex) and not is_inline(node, styles):
            if event == "start":
                flush_line()
                if text_content:
                    text = text_content.strip()
                    if text:
                        lines.append([{
                            "text": text, 
                            "indent": current_indent,
                            "bold": text_style['bold'],
                            "italic": text_style['italic'],
                            "underline": text_style['underline']
                        }])
            elif event == "end":
                flush_line()
        elif event == "start" and text_content:
            text = text_content.strip()
            if text:
                current_line.append(text)
                current_style = text_style
    
    flush_line()
    return lines


# Usage:
tree = HTMLParser(open('10k/bumble.html').read())
s = time()
reduced_form = html_reduction(tree)
print(f"Processing time: {time()-s:.3f} seconds")
format_list_html(reduced_form)