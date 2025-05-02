import webbrowser
import os

def visualize_dict(doc_dict):
    """
    Visualize the document dictionary with simple indentation.
    """
    html_content = """
    <html>
    <head>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; }
            div { margin: 5px 0; }
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
            else:
                # This is a heading
                result += f'<div style="margin-left:{indent}px">{key}</div>\n'
                
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