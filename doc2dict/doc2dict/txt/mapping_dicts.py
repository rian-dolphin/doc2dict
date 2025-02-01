dict_10k = {
    "rules": {
        "remove": [
            {
                "pattern": "<PAGE>",
                "match_type": "exact"
            }
        ],
        "mappings": [
            {
                "type": "hierarchy",
                "name": "part",
                "pattern": r"^PART\s",
                "hierarchy": 0
            },
            {
                "type": "hierarchy",
                "name": "item",
                "pattern": r"^ITEM\s",
                "hierarchy": 1
            },
            {
                "name": "table",
                "pattern": r"^<TABLE>",
                "end": r"^</TABLE>"
            },
            {
                "name": "caption",
                "pattern": r"^<CAPTION>",
                "end": r"^<S>"
            },
            {
                "name": "footnote",
                "pattern": r"^<FN>",
                "end": r"^</FN>"
            }
        ]
    }
}