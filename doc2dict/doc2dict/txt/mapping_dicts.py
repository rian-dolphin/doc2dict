
dict_sgml = {
    "rules": {
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
                "pattern": r"^ITEM\s",
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
            "text_pattern": r"^ITEM\s+(\d+|ONE|TWO|THREE|FOUR|FIVE|SIX|SEVEN|EIGHT|NINE|TEN)"
        },
        "output": {
            "format": "item{}",
            "field": "text"  # Could also be "text" or any other field name
        }
    }
]