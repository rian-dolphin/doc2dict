from html_parser import html_reduction
from visualizer import format_list_html
from time import time
from selectolax.parser import HTMLParser
import os
import webbrowser


#downloader = PremiumDownloader()
#downloader.download_submissions(filing_date='2021-12-30',submission_type=['10-K'],output_dir='10k/2021_12_31')

# now we can process the files in the output directory

with open('10k/2021_12_31/000149315221032816/form10-k.htm', 'r') as f:
    html = f.read()
    tree = HTMLParser(html)
    s = time()
    reduced_form = html_reduction(tree)
    print(f"Processing time: {time()-s:.3f} seconds")
    webbrowser.open('file:///C:/Users/jgfri/OneDrive/Desktop/Generalized%20Parsers/10k/2021_12_31/000149315221032816/form10-k.htm')
    format_list_html(reduced_form)


# portfolio = Portfolio('10k/2021_12_31')
# for submission in portfolio:
#     for tenK in submission.document_type(['10-K']):
#         with open(tenK.filename, 'r') as f:
#             html = f.read()
#             tree = HTMLParser(html)
#             s = time()
#             reduced_form = html_reduction(tree)
#             print(f"Processing time: {time()-s:.3f} seconds")
#             webbrowser.open(tenK.filename)
#             format_list_html(reduced_form)
#             raise SystemExit
            

