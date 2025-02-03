mapping update robustness
* for txt switch to '\n' before and after header


for tmrw
we need to fix trim
{
    "type": "trim",
    "match": {
        "type": "part",  # looking for part sections
        "expected": 1    # we expect 1 occurrence
    },
    "output": {
        "type": "introduction"  # wrap previous content as introduction
    }
}

how it should work is that we find first type = part, get text, and check for duplicates 
if more than expected, we take up to tje trim before one (e.g. if 1 we take the first one)
and send it and everything before it to the type in this case introduction with content