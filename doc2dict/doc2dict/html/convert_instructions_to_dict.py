import re
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
    hierarchy_dict = {('bold','class:part'):1}
    current_idx = 'base'
    # might have issue here due to some lines having multiple stuff
    for idx,instructions in enumerate(instructions_list):
        instruction = instructions[0]
        if 'text' in instruction:
            text = instruction['text'].lower()
            text = instruction['text'].lower()

            if re.search(r'^part\s*([ivx]+)$', text):
                header_tuple = ('bold','class:part')
                current_idx = idx
                dct[current_idx] = {'title':text,'contents':[]}

                #print(hierarchy_dict.get(header_tuple,None))
            
        for instruction in instructions:
            dct[current_idx]['contents'].append(instruction)

    return dct
   