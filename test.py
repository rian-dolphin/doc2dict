from html_parser import html_reduction
from visualizer import format_list_html
from time import time
from selectolax.parser import HTMLParser
import os
import webbrowser


def process_submission(sub):
    for doc in sub.document_type(['10-K']):
        with open(doc.path, 'r') as f:
            html = f.read()
        tree = HTMLParser(html)
        reduced_form = html_reduction(tree)


with open('10k/2021_12_31/000149315221032816/form10-k.htm', 'r') as f:
    html = f.read()
    tree = HTMLParser(html)
    s = time()
    reduced_form = html_reduction(tree)
    print(f"Processing time: {time()-s:.3f} seconds")
    webbrowser.open('file:///C:/Users/jgfri/OneDrive/Desktop/Generalized%20Parsers/10k/2021_12_31/000149315221032816/form10-k.htm')
    format_list_html(reduced_form)

#from datamule import Portfolio
#portfolio = Portfolio('10k/dec24')
#portfolio.download_submissions(submission_type=['10-K'],filing_date=('2024-12-01','2024-12-31'))
#portfolio.process_submissions(process_submission)


