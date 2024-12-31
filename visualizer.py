import webbrowser
import os

def format_list_html(nested_list):
    # Create HTML content
    html_content = """
<html>
<body>
"""
    
    for items in nested_list:
        if isinstance(items, list):
            html_content += "<div>\n"
            for item in items:
                html_content += f"    <span style='margin-right: 20px;'>{str(item)}</span>\n"
            html_content += "</div>\n</br>"
        else:
            html_content += f"<div>{str(items)}</div>\n</br>"
    
    html_content += """
</body>
</html>
"""
    
    # Write HTML content to a temporary file
    with open('temp.html', 'w',encoding='utf-8') as f:
        f.write(html_content)
    
    # Get the absolute path of the file
    file_path = os.path.abspath('temp.html')
    
    # Open the HTML file in the default web browser
    webbrowser.open('file://' + file_path)
