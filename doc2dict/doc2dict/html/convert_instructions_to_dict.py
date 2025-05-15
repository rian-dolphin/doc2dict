import re
import pkg_resources

version = pkg_resources.get_distribution("doc2dict").version
# identify  font-sizes
# strip normal + subscript
# so now we have poss headers
# we can consider first item of every instruction 

# for here, regex should grab like most attributes or something
# def determine_hierarchy(instructions_list,mapping_dict):
#     return
#     return {("regex:r'part\s*([0-9]+)'") : 1}
#     pass
    #     hierarchy_dict = {1: [('bold','regex:part')]}
    # should return the hierarchy of the instructions based on attributes

def convert_instructions_to_dict(instructions_list):
    dct = {'base':{'contents':[]}}
    hierarchy_dict = {('bold','class:part'):0,
                      ('bold','class:signatures'):0,
                      ('bold','class:item'):1}
    current_idx = 'base'
    current_hierarchy = 0
    # might have issue here due to some lines having multiple stuff
    for idx,instructions in enumerate(instructions_list):
        instruction = instructions[0]
        if 'text' in instruction:
            text = instruction['text'].lower()
            text = instruction['text'].lower()

            regex_tuples = [(r'^part\s*([ivx]+)$','part'),(r'^signatures?\.*$','signatures'),(r'^item\s*(\d+)','item')]
            for regex, header in regex_tuples:
                if re.match(regex,text):
                    attribute = 'bold'
                    hierachy = hierarchy_dict.get((attribute,f"class:{header}"),None)
                    if hierachy is not None:
                        print(header)
                    current_idx = idx
                    dct[current_idx] = {'title':text,'class':header,'contents':[]}
                    continue
            
        for instruction in instructions:
            if current_idx == idx:
                # skip section header
                continue
            dct[current_idx]['contents'].append(instruction)

    dct = {'metadata':{'parser':'doc2dict','github':'https://github.com/john-friedman/doc2dict','version':version}, 'document':dct}
    return dct
   