from .reducer import html_reduction
from .constructer import construct_dict
from .mapping import map_dict


def html2dict(content,mapping_dict=None):
    lines = html_reduction(content)
    dct = construct_dict(lines)
    dct = mapping(dct, mapping_dict)
    return dct