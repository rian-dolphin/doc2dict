import re

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

class Ctx:
    def __init__(self, base=16.0):
        self.base = base  # base font size
        self.vh = 900     # viewport height
        self.vw = 1600    # viewport width
        self.current_font_size = base  # Track current font size

class Box:
    def __init__(self):
        self.mt = self.mb = self.pt = self.pb = self.bt = self.bb = 0  # margins, padding, borders
        self.ch = 0  # content height
    
    @property
    def height(self):
        return self.mt + self.pt + self.bt + self.ch + self.mb + self.pb + self.bb

def parse_val(val, ctx, parent_size=None):
    """Parse CSS values with unit support"""
    if not val or val == 'auto' or val == 'none': 
        return 0
    
    try:
        m = re.match(r'^(-?\d*\.?\d+)(\D*)$', val.strip())
        if not m: 
            return 0
        
        n, u = float(m.group(1)), m.group(2)
        
        # If parent_size is not provided, use current context font size
        if parent_size is None:
            parent_size = ctx.current_font_size
            
        units = {
            '': n,
            'px': n,
            'em': n * parent_size,
            'rem': n * ctx.base,
            '%': (n/100) * parent_size,
            'vh': (n/100) * ctx.vh,
            'vw': (n/100) * ctx.vw,
            'pt': n * 1.333333,
            'pc': n * 16,
            'in': n * 96,
            'cm': n * 37.795276,
            'mm': n * 3.779528
        }
        
        return units.get(u, 0)
    except:
        return 0

def parse_border(val, ctx, parent_size=None):
    """Parse border values"""
    if not val: 
        return 0
    return next((parse_val(p, ctx, parent_size) for p in val.split() if re.match(r'^\d', p)), 0)

def calc_line_height(fs, lh):
    """Calculate line height"""
    if not lh: 
        return fs  # Default to font size
    
    try:
        if isinstance(lh, (int, float)):
            return fs * float(lh)  # multiplier
        elif lh.endswith('px'):
            return float(lh[:-2])
        elif lh.endswith('%'):
            return fs * (float(lh[:-1])/100)
        return fs  # Default to font size for any other value
    except:
        return fs

def get_node_styles(node):
    style = node.attributes.get('style')
    if not style:
        return {}
    return standardize_css(style)

def get_text_style(node, styles):
    text_style = {
        'bold': False,
        'italic': False,
        'underline': False
    }
    
    if node.tag in {'b', 'strong'}: 
        text_style['bold'] = True
    if node.tag in {'i', 'em'}: 
        text_style['italic'] = True
    if node.tag == 'u': 
        text_style['underline'] = True
        
    font_weight = styles.get('font-weight', [''])[0]
    if font_weight in {'bold', '700', '800', '900'}:
        text_style['bold'] = True
        
    if styles.get('font-style', [''])[0] == 'italic':
        text_style['italic'] = True
        
    if 'underline' in styles.get('text-decoration', [''])[0]:
        text_style['underline'] = True
        
    return text_style

def is_inline(node, styles):
    if node.tag in {'span', 'a', 'strong', 'em', 'b', 'i', 'u'}:
        return True
    return styles.get('display', [''])[0] == 'inline'

def standardize_css(style):
    if not style: 
        return {}
    return {
        k.strip(): v.strip().split() 
        for k, v in (pair.split(':') for pair in style.split(';') if ':' in pair)
        if k.strip() and v.strip()
    }

def compute_font_size(styles, ctx, parent_size=None):
    """Compute font size correctly based on CSS inheritance"""
    if parent_size is None:
        parent_size = ctx.base
        
    font_size = parent_size  # Start with parent size

    if 'font-size' in styles:
        font_size_value = styles['font-size'][0]
        
        # Handle keywords
        keywords = {
            'xx-small': ctx.base * 0.6,
            'x-small': ctx.base * 0.75,
            'small': ctx.base * 0.889,
            'medium': ctx.base,
            'large': ctx.base * 1.2,
            'x-large': ctx.base * 1.5,
            'xx-large': ctx.base * 2.0,
            'smaller': parent_size * 0.8,
            'larger': parent_size * 1.2
        }
        
        if font_size_value in keywords:
            font_size = keywords[font_size_value]
        else:
            font_size = parse_val(font_size_value, ctx, parent_size)
    
    return font_size

def get_box_metrics(styles, ctx, parent_size=None):
    """Calculate box model metrics"""
    if parent_size is None:
        parent_size = ctx.current_font_size
        
    # Compute font size for this element
    fs = compute_font_size(styles, ctx, parent_size)
    
    # Update context with current font size
    ctx.current_font_size = fs
    
    box = Box()
    
    # Get box properties
    props = {
        'margin-top': 'mt', 'margin-bottom': 'mb',
        'padding-top': 'pt', 'padding-bottom': 'pb'
    }
    
    for css_prop, box_prop in props.items():
        if css_prop in styles:
            setattr(box, box_prop, parse_val(styles[css_prop][0], ctx, fs))
    
    # Borders
    if 'border-top' in styles: 
        box.bt = parse_border(styles['border-top'][0], ctx, fs)
    if 'border-bottom' in styles: 
        box.bb = parse_border(styles['border-bottom'][0], ctx, fs)
    
    # Get line height
    line_height = styles.get('line-height', [''])[0]
    box.ch = calc_line_height(fs, line_height)
    
    # Handle border-box
    if styles.get('box-sizing', [''])[0] == 'border-box':
        extra = box.pt + box.pb + box.bt + box.bb
        box.ch = max(0, box.ch - extra)
    
    return box, fs

def process_height(node, styles, ctx, parent_size=None):
    """Process element height"""
    if parent_size is None:
        parent_size = ctx.current_font_size
        
    box, fs = get_box_metrics(styles, ctx, parent_size)
    
    return {
        'font_size': round(fs, 2),
        'content_height': round(box.ch, 2),
        'total_height': round(box.height, 2),
        'box': {
            'mt': round(box.mt, 2),
            'mb': round(box.mb, 2),
            'pt': round(box.pt, 2),
            'pb': round(box.pb, 2),
            'bt': round(box.bt, 2),
            'bb': round(box.bb, 2)
        }
    }

def html_reduction(tree):
    """Main processing function"""
    ctx = Ctx()
    blocks = {'p', 'div', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'article', 'section', 'li'}
    skip = {'script', 'style', 'noscript'}
    lines = []
    cur_line = []
    row_items = []
    in_row = False
    
    # Track parent font sizes for inheritance
    parent_font_sizes = {}
    current_parent_id = None
    
    def flush():
        if cur_line:
            items = []
            for text, style, node, parent_size in cur_line:
                if text.strip():
                    metrics = process_height(node, get_node_styles(node), ctx, parent_size)
                    items.append({
                        "text": text.strip(),
                        "bold": style.get('bold', False),
                        "italic": style.get('italic', False),
                        "underline": style.get('underline', False),
                        "height": metrics['total_height'],
                        "font_size": metrics['font_size']
                    })
            if items: 
                lines.append(items)
            cur_line.clear()

    current_parent_stack = []
    
    for event, node, styles, text, style in iterwalk(tree.body, include_text=True):
        if node.tag in skip: 
            continue
        
        node_id = id(node)
        
        if event == "start":
            # Push parent tracking
            if current_parent_id is not None:
                current_parent_stack.append(current_parent_id)
                parent_size = parent_font_sizes.get(current_parent_id, ctx.base)
            else:
                parent_size = ctx.base
            
            # Calculate this node's font size
            font_size = compute_font_size(styles, ctx, parent_size)
            parent_font_sizes[node_id] = font_size
            current_parent_id = node_id
            
        if node.tag == 'tr':
            if event == "start":
                in_row = True
                row_items = []
            elif event == "end":
                if row_items:
                    row_metrics = []
                    for t, s, n, p_size in row_items:
                        metrics = process_height(n, get_node_styles(n), ctx, p_size)
                        row_metrics.append({
                            "text": t,
                            "bold": s['bold'],
                            "italic": s['italic'],
                            "underline": s['underline'],
                            "height": metrics['total_height'],
                            "font_size": metrics['font_size']
                        })
                    if row_metrics:
                        lines.append(row_metrics)
                in_row = False
                row_items = []
                
        if in_row and event == "start" and text:
            t = text.strip()
            if t:
                parent_size = parent_font_sizes.get(current_parent_stack[-1] if current_parent_stack else None, ctx.base)
                row_items.append((t, style, node, parent_size))
            continue
            
        if (node.tag in blocks or styles.get('display', [''])[0] == 'flex') and not is_inline(node, styles):
            if event == "start":
                flush()
                if text:
                    t = text.strip()
                    if t:
                        parent_size = parent_font_sizes.get(current_parent_stack[-1] if current_parent_stack else None, ctx.base)
                        metrics = process_height(node, styles, ctx, parent_size)
                        lines.append([{
                            "text": t,
                            "bold": style['bold'],
                            "italic": style['italic'],
                            "underline": style['underline'],
                            "height": metrics['total_height'],
                            "font_size": metrics['font_size']
                        }])
            elif event == "end":
                flush()
        elif event == "start" and text:
            t = text.strip()
            if t:
                parent_size = parent_font_sizes.get(current_parent_stack[-1] if current_parent_stack else None, ctx.base)
                cur_line.append((t, style, node, parent_size))
                
        if event == "end":
            # Pop parent tracking
            if current_parent_stack:
                current_parent_id = current_parent_stack.pop()
            else:
                current_parent_id = None
    
    flush()
    return lines