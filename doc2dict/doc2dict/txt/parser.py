from doc2dict.mapping import DocumentProcessor


def txt2dict(content,mapping_dict):
    # first split the content into lines
    lines = content.split('\n')

    processor = DocumentProcessor(mapping_dict)
    result = processor.process(lines)
    return result