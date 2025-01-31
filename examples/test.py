from doc2dict.xml_mapping_dicts import dict_345
from doc2dict import parse_xml
import json

with open('../samples/tsla4.xml') as f:
    content = f.read()

transformed_data = parse_xml(content, mapping_dict=dict_345)

with open('tsla4.json', 'w', encoding='utf-8') as f:
    json.dump(transformed_data, f, indent=4)