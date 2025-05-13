# HTML


Target Benchmark:
~200 pages per second, single threaded.

# To work on:
* Merge lines - should accept italic if within line.
* Merge across lines
* indent


## Table
* ah so whats going on is rowspan
hmm so new approach
figure out the matrix
 - then apply smart cleaning, like subsets, header detect
 - but first just get full matrix.

 isssue is one matrix size - we dont know it before iteration
 two is assignment

actually no - we know number of columns at start. (so we assume this is standard, in a fail soft way)

yeah so what we do is populate as we go
if rowspan, create that many lines


* better:
* Fake Table detection
* '(' and ')'