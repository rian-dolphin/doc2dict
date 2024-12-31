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

        yield ("start", node, current_styles, text_content)
        for child in node.iter(include_text=include_text):
            if child is not node:
                yield from walk(child, current_styles)
        yield ("end", node, current_styles, text_content)
    
    for node in root.iter(include_text=include_text):
        if node is not root:
            yield from walk(node)

def is_inline(node, styles):
    if node.tag in {'span', 'a', 'strong', 'em', 'b', 'i'}:
        return True
    display = styles.get('display', [''])[0]
    # flex should NOT be treated as inline
    return display == 'inline'

def html_reduction(tree):
    blocks = {'p', 'div', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'article', 'section', 'li'}
    skip_elements = {'script', 'style', 'noscript'}
    lines = []
    current_line = []
    row_content = []
    in_row = False
    
    def flush_line():
        if current_line:
            items = [item.strip() for item in current_line if item.strip()]
            if items:
                lines.append(items)
            current_line.clear()

    for event, node, styles, text_content in iterwalk(tree.body, include_text=True):
        if node.tag in skip_elements:
            continue

        # Handle flex containers
        is_flex = styles.get('display', [''])[0] == 'flex'
        
        # Handle table rows
        if node.tag == 'tr':
            if event == "start":
                in_row = True
                row_content = []
            elif event == "end":
                if row_content:
                    lines.append(row_content)
                in_row = False
                row_content = []
                continue

        # If we're in a table row, collect all text
        if in_row and event == "start" and text_content:
            text = text_content.strip()
            if text:
                row_content.append(text)
            continue
            
        # Normal block and flex handling
        if (node.tag in blocks or is_flex) and not is_inline(node, styles):
            if event == "start":
                flush_line()
                if text_content:
                    text = text_content.strip()
                    if text:
                        lines.append([text])
            elif event == "end":
                flush_line()
        elif event == "start" and text_content:
            text = text_content.strip()
            if text:
                current_line.append(text)
    
    flush_line()
    return lines
# Usage:
if __name__ == "__main__":
    tree = HTMLParser(open('10k/bumble.html').read())
    s = time()
    reduced_form = html_reduction(tree)
    print(f"Processing time: {time()-s:.3f} seconds")
    format_list_html(reduced_form)