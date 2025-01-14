import xmltodict
import json


# Or directly from a file
with open('test.xml') as f:
    data_dict = xmltodict.parse(f.read())


with open('parsed.json', 'w') as json_file:
    json.dump(data_dict, json_file, indent=4)
