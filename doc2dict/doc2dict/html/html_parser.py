import re

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

class Ctx:
    def __init__(self, base=16.0):
        self.base = base  # base font size
        self.vh = 900    # viewport height
        self.vw = 1600   # viewport width

class Box:
    def __init__(self):
        self.mt = self.mb = self.pt = self.pb = self.bt = self.bb = 0  # margins, padding, borders
        self.ch = 0  # content height
    
    @property
    def height(self):
        return self.mt + self.pt + self.bt + self.ch + self.mb + self.pb + self.bb

def parse_val(val, ctx, parent):
    """Parse CSS values with unit support"""
    if not val or val == 'auto' or val == 'none': return 0
    
    try:
        m = re.match(r'^(-?\d*\.?\d+)(\D*)$', val.strip())
        if not m: return 0
        
        n, u = float(m.group(1)), m.group(2)
        
        units = {
            '': n,
            'px': n,
            'em': n * parent,
            'rem': n * ctx.base,
            '%': (n/100) * parent,
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

def parse_border(val, ctx, parent):
    """Parse border values"""
    if not val: return 0
    return next((parse_val(p, ctx, parent) for p in val.split() if re.match(r'^\d', p)), 0)

def calc_line_height(fs, lh):
    """Calculate line height"""
    if not lh: return fs  # Default to font size
    
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

class StyleChain:
    def __init__(self, ctx):
        self.ctx = ctx
        self.chain = []
    
    def push(self, s): self.chain.append(s)
    def pop(self): self.chain.pop() if self.chain else None
    
    def get(self, prop, default=''):
        """Get computed style"""
        for s in reversed(self.chain):
            if prop in s: return s[prop][0]
        return default
    
    def font_size(self):
        """Calculate font size through chain"""
        size = self.ctx.base
        for s in self.chain:
            if 'font-size' in s:
                size = parse_val(s['font-size'][0], self.ctx, size)
        return size

def get_box_metrics(styles, chain):
    """Calculate box model metrics"""
    ctx = chain.ctx
    fs = chain.font_size()
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
    if 'border-top' in styles: box.bt = parse_border(styles['border-top'][0], ctx, fs)
    if 'border-bottom' in styles: box.bb = parse_border(styles['border-bottom'][0], ctx, fs)
    
    # Content height
    box.ch = calc_line_height(fs, chain.get('line-height'))
    
    # Handle border-box
    if chain.get('box-sizing') == 'border-box':
        extra = box.pt + box.pb + box.bt + box.bb
        box.ch = max(0, box.ch - extra)
    
    return box

def process_height(node, chain):
    """Process element height"""
    styles = get_node_styles(node)
    chain.push(styles)
    
    try:
        box = get_box_metrics(styles, chain)
        fs = chain.font_size()
        
        return {
            'font_size': round(fs, 2),
            'content_height': round(box.ch, 2),
            'total_height': round(box.ch, 2),  # Only use content height
            'box': {
                'mt': 0, 'mb': 0,
                'pt': 0, 'pb': 0,
                'bt': 0, 'bb': 0
            }
        }
    finally:
        chain.pop()

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
    
    if node.tag in {'b', 'strong'}: text_style['bold'] = True
    if node.tag in {'i', 'em'}: text_style['italic'] = True
    if node.tag == 'u': text_style['underline'] = True
        
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

def html_reduction(tree):
    """Main processing function"""
    ctx = Ctx()
    chain = StyleChain(ctx)
    blocks = {'p', 'div', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'article', 'section', 'li'}
    skip = {'script', 'style', 'noscript'}
    lines = []
    cur_line = []
    row_items = []
    in_row = False
    
    def flush():
        if cur_line:
            items = []
            for text, style, node in cur_line:
                if text.strip():
                    metrics = process_height(node, chain)
                    items.append({
                        "text": text.strip(),
                        "bold": style.get('bold', False),
                        "italic": style.get('italic', False),
                        "underline": style.get('underline', False),
                        "height": metrics['total_height'],
                        "font_size": metrics['font_size']
                    })
            if items: lines.append(items)
            cur_line.clear()

    for event, node, styles, text, style in iterwalk(tree.body, include_text=True):
        if node.tag in skip: continue
        
        if event == "start": chain.push(styles)
        
        if node.tag == 'tr':
            if event == "start":
                in_row = True
                row_items = []
            elif event == "end":
                if row_items:
                    lines.append([{
                        "text": t,
                        "bold": s['bold'],
                        "italic": s['italic'],
                        "underline": s['underline'],
                        "height": process_height(n, chain)['total_height'],
                        "font_size": process_height(n, chain)['font_size']
                    } for t, s, n in row_items])
                in_row = False
                row_items = []
                
        if in_row and event == "start" and text:
            t = text.strip()
            if t: row_items.append((t, style, node))
            continue
            
        if (node.tag in blocks or styles.get('display', [''])[0] == 'flex') and not is_inline(node, styles):
            if event == "start":
                flush()
                if text:
                    t = text.strip()
                    if t:
                        metrics = process_height(node, chain)
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
            if t: cur_line.append((t, style, node))
                
        if event == "end": chain.pop()
    
    flush()
    return lines