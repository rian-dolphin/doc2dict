import webbrowser
import os

def visualize_dict(doc_dict):
    """
    Visualize the document dictionary with simple indentation and level information.
    """
    html_content = """
    <html>
    <head>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; }
            div { margin: 5px 0; }
            .level-info { color: #666; font-size: 0.8em; margin-left: 5px; }
            .level-desc { color: #888; font-size: 0.8em; display: block; margin-top: 2px; margin-left: 20px; }
            .heading { font-weight: bold; }
        </style>
    </head>
    <body>
    """
    
    def process_dict(d, level=0):
        result = ""
        indent = level * 20  # 20px indent per level
        
        for key, value in d.items():
            if key == 'text':
                # This is content text
                result += f'<div style="margin-left:{indent}px">{value}</div>\n'
            elif key == 'level' or key == 'leveldesc':
                # Skip level and leveldesc as they'll be displayed with their parent
                continue
            else:
                # This is a heading
                # Check if there are level attributes
                level_info = ""
                level_desc = ""
                
                if isinstance(value, dict):
                    if 'level' in value:
                        level_info = f'<span class="level-info">(Level: {value["level"]})</span>'
                    if 'leveldesc' in value:
                        level_desc = f'<div class="level-desc">{value["leveldesc"]}</div>'
                
                result += f'<div style="margin-left:{indent}px"><span class="heading">{key}</span> {level_info}{level_desc}</div>\n'
                
                # Process the nested dictionary
                if isinstance(value, dict):
                    result += process_dict(value, level + 1)
        
        return result
    
    # Start processing from the document key
    if 'document' in doc_dict:
        html_content += process_dict(doc_dict['document'])
    else:
        html_content += process_dict(doc_dict)
    
    html_content += """
    </body>
    </html>
    """
    
    # Write HTML content to a temporary file
    with open('doc_structure.html', 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    # Get the absolute path of the file
    file_path = os.path.abspath('doc_structure.html')
    
    # Open the HTML file in the default web browser
    webbrowser.open('file://' + file_path)
    
    return "Visualization opened in browser"