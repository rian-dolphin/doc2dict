I want to expand my engine from being able to do 

dict_345 = {
    "transformations": [
        {
            "search": {
                "key": "footnoteId",
                "identifier": "@id"
            },
            "match": {
                "identifier": "@id",
                "content": "#text",
                "remove_after_use": True 
            },
            "output": {
                "key": "footnote",
                "value": "content"
            }
        }
    ]
}

to do 'rules'

rules are a special thing that happens before transformations. it is used to convert items in a list into a dictionary that we can then apply transformations on etc. For now, assume each item in list is a line like "the day I grew up" or "<PAGE>"

regex matches should be setup

there are several types of rules:

* remove
e.g. remove '<PAGE>' with option for 'exact' or 'strip'
* detect_start

* mappings
defines section headers
e.g. find all lines that begin with PART, set hierarchy to 0 (top) (PART I BIZNESS)
e.g. find all lines that begin with ITEM, set hierarchy to 1 (ITEM 1 RISKY STUFF)

and then by default (no logic needed this is assumed) lines that are not header are assigned under most recent header

e.g.
{'text':'PART I BIZNESS',type='part',content={'text':'ITEM 1 RISKY STUFF', type 'item', content = 'the context of the next lines before next item'}}

Note: we will later want to make sure transformations can take regex to match patterns defined by user such as ITEM ONE, ITEM 1 ...
etc to cast to a standardized value like 'item1'

there is also another type of mapping with defined start /end

e.g. caption would be setup to get until starts with <S>

<TABLE>
<CAPTION>

                                            Quarter                    Year Ended
1995                          First    Second    Third     Fourth       June 30
----                          -----    ------    -----     -------     ----------
<S>                          <C>       <C>      <C>       <C>          <C>

Net Sales                   $14,027   $15,821   $19,750   $21,515      $71,113
Gross Profit                  4,385     5,052     6,762     7,372       23,571
Income From
  Continuing Operations     $   715   $ 3,084(1)$   683(2)$ 2,105(2)   $ 6,587(1)(2)
Income From Discontinued
  Operations                   -         -         -          462          462
                            -------   -------   -------   -------      -------  
Net Income                  $   715   $ 3,084   $   683   $ 2,567      $ 7,049
                            =======   =======   =======   =======      =======  
Income Per Share:
  Primary:
    Continuing Operations    $ .06     $ .25(1) $ .06(2)  $ .17(2)     $ .53(1)(2)
    Discontinued Operations     -         -         -       .04          .04
                             -----     -----    -----     -----        -----      
    Net Income               $ .06     $ .25    $ .06     $ .21        $ .57
                             =====     =====    =====     =====        ===== 
  Fully Diluted:
    Continuing Operations    $ .06     $ .23(1) $ .06(2)  $ .16(2)     $ .52(1)(2)
    Discontinued Operations     -         -         -       .03          .03
                            ------     -----    -----     -----        -----
   Net Income                $ .06     $ .23    $ .06     $ .19        $ .55
                            ======     =====    =====     =====        =====

<FN>

(1) Includes  $2,000,000 ($.14 per share fully diluted and $.16 primary) for the
    quarter  ended  December  31, 1994 and year ended June 30, 1995 of insurance
    proceeds received on the death of the former chairman.

(2) Includes a $1,494,000 net of tax restructuring  charge ($.10 per share fully
    diluted  and  $.12  primary)  for the  year  ended  June  30,  1995  for the
    consolidation  of the  Company's  Puerto Rican  operation  into its domestic
    facilities.  The net of tax  charge  was  $1,035,000  ($.07 per share  fully
    diluted and $.08  primary)  and $459,000  ($.03 per share fully  diluted and
    $.04  primary)  for the  quarters  ended March 31,  1995 and June 30,  1995,
    respectively.

</FN>
</TABLE>

* processing (e.g. tables)
needs to be able to find start of pattern e.g.
<CAPTION>

