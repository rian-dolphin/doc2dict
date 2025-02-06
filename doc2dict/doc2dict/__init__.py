from .html.html_parser import html_reduction
from .html.visualizer import format_list_html
from .xml.parser import xml2dict
from .txt.parser import txt2dict
from .dict2dict import dict2dict

__all__ = ['html_reduction', 'format_list_html', 'xml2dict', 'txt2dict','dict2dict']