import webbrowser
import os

def format_list_html(nested_list):
    # Define a list of pleasing background colors for multi-item rows
    colors = ['#F3E6FF', '#FFE6E6', '#E6FFE6', '#FFE6F3', '#E6FFFF', '#FFF3E6']
    
    # Define a distinct color for single items
    # Using a soft purple that's different from the other colors but still pleasing
    single_item_color = '#E6F3FF'
    
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
    }
</style>
</head>
<body>
"""
    
    for items in nested_list:
        if isinstance(items, list):
            # Get the indent from the first item if it exists
            first_indent = items[0].get('indent', 0) if isinstance(items[0], dict) else 0
            html_content += f"<div class='row' style='padding-left: {first_indent}em'>\n"
            
            # If it's a single item in a list, use the single item color
            if len(items) == 1:
                color = single_item_color
            else:
                color = colors[0]  # Start with first color
                
            for i, item in enumerate(items):
                if len(items) > 1:
                    color = colors[i % len(colors)]  # Only cycle colors for multi-item rows
                if isinstance(item, dict):
                    text = item.get('text', '')
                else:
                    text = str(item)
                html_content += f"    <span class='item' style='background-color: {color}'>{text}</span>\n"
            
            html_content += "</div>\n"
        else:
            # Handle single item case
            if isinstance(items, dict):
                text = items.get('text', '')
                indent = items.get('indent', 0)
            else:
                text = str(items)
                indent = 0
                
            html_content += f"<div class='row' style='padding-left: {indent}em'><span class='item' style='background-color: {single_item_color}'>{text}</span></div>\n"
    
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