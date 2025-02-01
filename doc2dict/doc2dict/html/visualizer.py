import webbrowser
import os

def format_list_html(nested_list):
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
    
    for items in nested_list:
        if isinstance(items, list):
            first_indent = items[0].get('indent', 0) if isinstance(items[0], dict) else 0
            html_content += f"<div class='row' style='padding-left: {first_indent}em'>\n"
            
            for i, item in enumerate(items):
                # Single item -> blue
                if len(items) == 1:
                    color = single_line_color
                # Multiple items: first -> green, rest -> red
                else:
                    color = multi_first_color if i == 0 else multi_rest_color
                    
                styled_text = get_styled_text(item)
                html_content += f"    <span class='item' style='background-color: {color}'>{styled_text}</span>\n"
            
            html_content += "</div>\n"
        else:
            if isinstance(items, dict):
                indent = items.get('indent', 0)
                styled_text = get_styled_text(items)
                height = items.get('height', '')
                height_style = f'height: {height};' if height else ''
                html_content += f"<div class='row' style='padding-left: {indent}em'><span class='item' style='background-color: {single_line_color}; {height_style}'>{styled_text}</span></div>\n"
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