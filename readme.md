# Generalized Parsers

This is a repo for parsing human readable datatypes into machine optimized form.

### Planned Parsers
1. HTML Parser
2. PDF/IMAGE Parser


### Strategy
1. Reduce form
2. Use rules to convert reduced form to hierarchies in nested json

### Add-ons
I'll work to make this optimized for SEC filings using mapping dicts

### Speed
* Don't worry too much about speed. under 1s for 100 pages is fine. with multiprocessing thats like 1000 pages / second. 
* If optimization matters, we will rewrite in C or Cython.

### Benchmarks
Bumble 10k
50ms to load, 80ms to iterate through

# note:
current issue is bold inheritance not working
todo writeup of how parser works
write up of rules
visualize ruleset

publish to python

Generalized-parser? or maybe miruvor 