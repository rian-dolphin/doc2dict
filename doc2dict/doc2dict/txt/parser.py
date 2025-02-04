from doc2dict.mapping import DocumentProcessor

def txt2dict(content,mapping_dict):
    # Split by double newlines to get paragraphs
    paragraphs = content.split('\n\n')
    
    # Process each paragraph
    lines = []
    for paragraph in paragraphs:
        if paragraph.strip():  # Skip empty paragraphs
            # Add double newlines if not already present
            processed =  paragraph.strip()
            processed = paragraph.split('\n')
            processed[0] = '\n' + processed[0]
            lines.extend(processed)
            
    processor = DocumentProcessor(mapping_dict)
    result = processor.process(lines)
    return result