import webbrowser
import os

def visualize_lines(nested_list):
    # Simplified color scheme
    single_line_color = '#E6F3FF'  # Blue hue
    multi_first_color = '#E6FFE6'  # Green hue
    multi_rest_color = '#FFE6E6'   # Red hue
    
    html_content = """
<html>
<head>
<style>
    body {
        font-family: Arial, sans-serif;
        line-height: 1.6;
        margin: 20px;
    }
    .row {
        margin-bottom: 20px;
        display: flex;
        flex-wrap: wrap;
    }
    .item {
        padding: 10px 15px;
        border-radius: 5px;
        margin-right: 15px;
        margin-bottom: 10px;
        display: inline-block;
    }
</style>
</head>
<body>
"""
    
    def get_styled_text(item):
        """Helper function to apply text styling"""
        if not isinstance(item, dict):
            return str(item)
            
        height = str(item.get('height', ''))
        text = item.get('text', '')
        style_properties = []
        
        if item.get('bold', False):
            style_properties.append('font-weight: bold')
        if item.get('italic', False):
            style_properties.append('font-style: italic')
        if item.get('underline', False):
            style_properties.append('text-decoration: underline')
        if height:  # Change height to font-size
            style_properties.append(f'font-size: {height}')
                
        if style_properties:
            return f"<span style='{'; '.join(style_properties)}'>{text}</span>"
        return text
    
    def convert_indent(px_value):
        """Convert pixel indent to appropriate em value"""
        # Assuming base font size is 16px, convert to em
        return px_value / 16 * 5
    
    for items in nested_list:
        if isinstance(items, list):
            # Get indent from first item
            first_item_indent = items[0].get('indent', 0) if isinstance(items[0], dict) else 0
            
            # Check if centered and set styles accordingly
            center_align = first_item_indent == 50
            if center_align:
                # For centered items, don't apply padding-left
                html_content += f"<div class='row' style='text-align: center; justify-content: center;'>\n"
            else:
                # For non-centered items, apply padding-left
                first_indent = convert_indent(first_item_indent)
                html_content += f"<div class='row' style='padding-left: {first_indent}em;'>\n"
            
            for i, item in enumerate(items):
                # Single item -> blue
                if len(items) == 1:
                    color = single_line_color
                # Multiple items: first -> green, rest -> red
                else:
                    color = multi_first_color if i == 0 else multi_rest_color
                
                # Get individual item indent if different from first item
                item_indent = 0
                item_raw_indent = item.get('indent', 0) if isinstance(item, dict) else 0
                
                # Special handling for individual items with indent = 50
                item_center_align = item_raw_indent == 50
                item_text_align = 'text-align: center;' if item_center_align else ''
                
                # Only calculate margin-left for non-centered items after the first item
                if i > 0 and isinstance(item, dict) and not item_center_align:
                    if center_align:
                        # If parent is centered but this item isn't, use its own indent
                        item_indent = convert_indent(item_raw_indent)
                    else:
                        # Normal case: calculate relative indent
                        first_indent = convert_indent(first_item_indent)
                        item_indent = convert_indent(item_raw_indent) - first_indent
                        if item_indent < 0:
                            item_indent = 0
                
                styled_text = get_styled_text(item)
                html_content += f"    <span class='item' style='background-color: {color}; margin-left: {item_indent}em; {item_text_align}'>{styled_text}</span>\n"
            
            html_content += "</div>\n"
        else:
            if isinstance(items, dict):
                item_raw_indent = items.get('indent', 0)
                styled_text = get_styled_text(items)
                height = items.get('height', '')
                height_style = f'height: {height};' if height else ''
                
                # Special handling for indent = 50
                center_align = item_raw_indent == 50
                
                if center_align:
                    # For centered items, don't apply padding-left
                    html_content += f"<div class='row' style='text-align: center;'><span class='item' style='background-color: {single_line_color}; {height_style}; text-align: center;'>{styled_text}</span></div>\n"
                else:
                    # For non-centered items, apply padding-left
                    indent = convert_indent(item_raw_indent)
                    html_content += f"<div class='row' style='padding-left: {indent}em;'><span class='item' style='background-color: {single_line_color}; {height_style};'>{styled_text}</span></div>\n"
            else:
                styled_text = str(items)
                indent = 0
                html_content += f"<div class='row' style='padding-left: {indent}em'><span class='item' style='background-color: {single_line_color}'>{styled_text}</span></div>\n"
    
    html_content += """
</body>
</html>
"""
    
    # Write HTML content to a temporary file
    with open('temp.html', 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    # Get the absolute path of the file
    file_path = os.path.abspath('temp.html')
    
    # Open the HTML file in the default web browser
    webbrowser.open('file://' + file_path)