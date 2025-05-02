from .reducer import html_reduction
from.constructer import construct_dict


def html2dict(content):
    lines = html_reduction(content)
    dct = construct_dict(lines)
    return dct