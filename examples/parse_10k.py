from doc2dict import html_reduction, format_list_html
from selectolax.parser import HTMLParser

# oh crap, I think we broke something weeks ago we didn't fix

        

with open('../samples/tsla10k.html', 'r') as f:
    tree = HTMLParser(f.read())
reduced_form = html_reduction(tree)

# save each item in the list to new line in a file
with open('tsla10k_reduced_form.txt', 'w',encoding='utf-8') as f:
    for item in reduced_form:
        f.write("%s\n" % item)
format_list_html(reduced_form)
