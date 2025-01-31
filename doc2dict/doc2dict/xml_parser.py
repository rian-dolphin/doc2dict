import xmltodict
from .mapping import JSONTransformer

def parse_xml(content, mapping_dict=None):
    data = xmltodict.parse(content)
    
    if mapping_dict is None:
        return data
     
    transformer = JSONTransformer(mapping_dict)
    transformed_data = transformer.transform(data)
    return transformed_data
