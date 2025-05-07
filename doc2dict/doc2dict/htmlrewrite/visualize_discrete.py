import webbrowser
import os

def format_dct_style(line):
    text = line['text']
    
    style_properties = []
    # might have issues here in the future
    if 'bold' in line:
        style_properties.append('font-weight: bold')
    if 'italic' in line:
        style_properties.append('font-style: italic')
    if 'underline' in line:
        style_properties.append('text-decoration: underline')
    if 'font-size' in line:
        font_size = line['font-size']
        if font_size:
            style_properties.append(f'font-size: {font_size}')


    return style_properties, text

def visualize_discrete(lines):
    # Simplified color scheme
    single_line_color = '#E6F3FF'  # Blue hue
    multi_first_color = '#E6FFE6'  # Green hue
    multi_rest_color = '#FFE6E6'   # Red hue
    table_color = '#FFE6FF'   # Purple hue
    
    html_content ="""
        <html>
        <head>
        <style>
        span {
  display: inline-block;
  }
        </style>
        </head>
        <body>"""
    
    for line in lines:
        div_style = ''
        if any(['text:center' in item for item in line]):
            div_style = 'text-align: center;'
        

        for idx, dct in enumerate(line):
            style_properties, text = format_dct_style(dct)
            if idx  == 0:
                html_content += f"<div style='{div_style}'>"

            if 'table' in dct:
                color = table_color
            elif len(line) == 1:
                color = single_line_color
            elif idx == 0:
                color = multi_first_color
            else:
                color = multi_rest_color
            
            style_properties += [f'background-color: {color}; margin-left:5px']
            style = '; '.join(style_properties)

            html_content += f"<span style='{style}'>{text}</span>"
            
        html_content += "</div>"
    
    html_content += """
        </body>
        </html>"""
    
    # Write HTML content to a temporary file
    with open('discrete.html', 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    # Get the absolute path of the file
    file_path = os.path.abspath('discrete.html')
    
    # Open the HTML file in the default web browser
    webbrowser.open('file://' + file_path)
        