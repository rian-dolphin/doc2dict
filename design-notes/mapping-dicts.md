mapping update robustness
* for txt switch to '\n' before and after header


for tmrw
we need to fix trim
{
        "type": "trim",
        "match": {
            "type": "part",  # or 'item'
            "expected": 1    # expected number of occurrences
        },
        "trim_before": 1,
        "output": {
            "type": "introduction"
        }
    }

how it should work is that we find first type = part, get text, and check for duplicates 
if more than expected, we take up to tje trim before one (e.g. if 1 we take the first one)
and send it and everything before it to the type in this case introduction with content