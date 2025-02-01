
dict_sgml = {
    "rules": {
        "join_text": "\n",
        "remove": [
            {
                "pattern": r"^<PAGE>",
            }
        ],
        "mappings": [
            {
                "name": "table",
                "pattern": r"^<TABLE>",
                "end": r"^</TABLE>"
            },
            {
                "name": "caption",
                "pattern": r"^<CAPTION>",
                "end": r"^<S>",
                "keep_end": True
            },
            {
                "name": "footnote",
                "pattern": r"^<FN>",
                "end": r"^</FN>"
            }
        ]
    }
}
        

dict_10k = dict_sgml
dict_10k["rules"]["mappings"].extend([            
    {
                "type": "hierarchy",
                "name": "part",
                "pattern": r"^\s*PART\s",
                "hierarchy": 0
            },
            {
                "type": "hierarchy",
                "name": "item",
                "pattern": r"^\s*ITEM\s",
                "hierarchy": 1
            },
            ])
    
# In the mapping dict:
dict_10k['transformations'] = [
    {
        "type": "standardize",
        "match": {
            "type": "part",
            "text_pattern": r"^\s*PART\s+([IVX]+)"
        },
        "output": {
            "format": "part{}",
            "field": "text"  # Where to store the standardized value
        }
    },
    {
        "type": "standardize", 
        "match": {
            "type": "item",
            "text_pattern": r"^\s*ITEM\s+(\d+|ONE|TWO|THREE|FOUR|FIVE|SIX|SEVEN|EIGHT|NINE|TEN)"
        },
        "output": {
            "format": "item{}",
            "field": "text"  # Could also be "text" or any other field name
        }
    },
    {
        "type": "merge_consecutive",
        "match": {
            "types": ["part", "item"]  # sections types to check for merging
        }
    },
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
    
]