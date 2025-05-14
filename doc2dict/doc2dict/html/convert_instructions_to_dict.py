
# identify  font-sizes
# strip normal + subscript
# so now we have poss headers
# we can consider first item of every instruction 

# hmm, we probably want to just do mapping dict first

# for tenk mapping
# part, item
tenk_mapping_dict = {
    1 : [
        {'class':'part','regex': r'part\s*([0-9]+)'},
    ],
    2 : [
        {'class':'item','regex': r'item\s*([0-9]+)'},
    ],
}
def determine_hierarchy(instructions_list,mapping_dict):
    pass
    #     hierarchy_dict = {1: [('bold','regex:part')]}
    # should return the hierarchy of the instructions based on attributes

def instructions_to_dict(instructions_list):
    # so this will just iterate through the hierarchy dict, it does like hierarchy_dict[(bold,regex,italic )] = 1
    # and then determine whether to append up or down

    # output will be like (numbers are line of instructions)
    # dct = {'1':{title='part 1,content : ['2': {'title':'item 1','content':[the red rabbit ate a cat.]}}}]}}
    pass
