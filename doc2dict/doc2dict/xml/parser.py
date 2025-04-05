import xmltodict
from ..mapping import JSONTransformer

def remove_namespace(path, key, value):
    # Remove namespace from keys
    if ':' in key:
        # Keep only the part after the last colon
        return key.split(':')[-1], value
    return key, value

def xml2dict(content, mapping_dict=None):

    data = xmltodict.parse(content,postprocessor=remove_namespace)

    if mapping_dict is None:
        return data
    
     
    transformer = JSONTransformer(mapping_dict)
    transformed_data = transformer.transform(data)
    return transformed_data
