import operator
from math import log2
from random import choice

def add_vectorn(a,b):
    return tuple(map(operator.add ,a,b ))

def add_vector3(a,b):
    return (a[0]+b[0],a[1]+b[1],a[2]+b[2])

# main wfc functions
def checkValidity(arena,constraints,position,structure,change):
    if len(position)==3:
        add_func=add_vector3
    else:
        add_func=add_vectorn

    for offset_key in constraints[structure]:
        n_position = add_func(position,offset_key)

        if (not n_position in change):
            # not changed + was good => still good
            continue

        if (not n_position in arena):
            # never changed => still good
            continue
        
        if (arena[n_position].isdisjoint(constraints[structure][offset_key])):
            return False
    return True

def propagate(arena,constraints,all_structure_set,position,choosen_structure):
    change={}
    to_be_updated=set()

    change[position]=arena[position]
    change[position].remove(choosen_structure)
    arena[position]={choosen_structure}

    # add position that may need to be changed due to removal of stuff at position. 
    for structure in change[position]:
        for offset_key in constraints[structure]:
            to_be_updated.add(tuple(map(operator.add,position,offset_key )))

    while len(to_be_updated)!=0:

        position = to_be_updated.pop()

        if not position in arena:
            arena[position]=all_structure_set.copy()

        for structure in arena[position]:
            if checkValidity(arena,constraints,position,structure,change):
                # still valid, doesn't need to be removed
                continue

            # if certain structure is invalid at this location, remove its possibility
            if not position in change:
                change[position]=set()
            change[position].add(structure)

            # since the information of this position changed, 
            # all positions that may depend on the invalidated structure 
            # also needs to be updated
            for key in constraints[structure]:
                n_position=tuple(map(operator.add ,position,key ))
                if not n_position in to_be_updated:
                    to_be_updated.add(n_position)
                    
        if position in change:
            arena[position].difference_update(change[position])

            # if no possibility is valid at the block, return false
            if(len(arena[position])==0):
                for key in change:
                    arena[key].update(change[key])
                return (False,None)

    return (True,change)

def extendConstraints(raw_constraints,all_structure_set,origin):

    # the following  generates extended constraints that can be infered from raw constraints.
    # this extended form is symmetric: all constrain information between two structure are stored for both structure.
    # this is not a foul proof method, but it does reduce the possibility by couple "hundred" folds.
    changed=set()


    extended_constraints={}
    for structure in raw_constraints: 
        extended_constraints[structure]={}
        for offset_key in raw_constraints[structure]:
            extended_constraints[structure][offset_key]=raw_constraints[structure][offset_key].copy()
        extended_constraints[structure][origin]={structure}

    # force symmetry at the beginning and reduce conditionals by half
    for structure in extended_constraints: 
        for offset_key in list(extended_constraints[structure].keys()):
            if offset_key==origin:continue
            changed.add((structure,offset_key))

            banned_structures = all_structure_set-extended_constraints[structure][offset_key]
            for banned_structure in banned_structures:
                reverse_offset_key = tuple(map(lambda x:-x, offset_key))
                if not reverse_offset_key in extended_constraints[banned_structure]:
                    extended_constraints[banned_structure][reverse_offset_key]=all_structure_set.copy()
                    
                if structure in extended_constraints[banned_structure][reverse_offset_key]:
                    extended_constraints[banned_structure][reverse_offset_key].remove(structure)

    while len(changed)!=0:
        # constraint changed for structure_a at intersection_rel_a
        # so, it is compared to all constraints
        structure_a,intersection_rel_a = changed.pop()

        for structure_b in extended_constraints:
            for intersection_rel_b in list(extended_constraints[structure_b].keys()):

                # since symmetry is forced in the beginning, now only half of the checks need to be done
                b_rel_a = tuple(map(operator.sub,intersection_rel_a,intersection_rel_b))

                if (b_rel_a in extended_constraints[structure_a] and not structure_b in extended_constraints[structure_a][b_rel_a]):continue

                # if not disjoint, this combination is still possible
                if not extended_constraints[structure_a][intersection_rel_a].isdisjoint(extended_constraints[structure_b][intersection_rel_b]):
                    continue

                a_rel_b = tuple(map(lambda x:-x,b_rel_a))

                # if it is marked as possible but is not possible anymore, change it.
                if not b_rel_a in extended_constraints[structure_a]:
                    extended_constraints[structure_a][b_rel_a]=all_structure_set.copy()
                if not a_rel_b in extended_constraints[structure_b]:
                    extended_constraints[structure_b][a_rel_b]=all_structure_set.copy()
                
                if structure_b in extended_constraints[structure_a][b_rel_a]:

                    extended_constraints[structure_a][b_rel_a].remove(structure_b)
                    extended_constraints[structure_b][a_rel_b].remove(structure_a)
                    changed.add((structure_a,b_rel_a))
                    changed.add((structure_b,a_rel_b))


    return extended_constraints

def solveWFC(raw_constraints,termination_count=1000):

    #intiation
    origin=None
    for structure in raw_constraints: 
        for key in raw_constraints[structure]:
            origin = tuple(map(lambda x:0,key))
            break
        if origin!=None:
            break
    
    all_structure_set = set(raw_constraints.keys())
 
    extended_constraints = extendConstraints(raw_constraints,all_structure_set,origin)

    arena={}
    arena[origin]=all_structure_set.copy()

    # below starts actual computation
    change_record=[{}]
    step_record=[]
    from alive_progress import alive_bar
    with alive_bar(termination_count, title='Processing', length=40,calibrate=50, bar='smooth',manual=True)  as bar:
        while True:
            if len(change_record)==0:
                print("rolling back further than history allows")
                raise Exception
            position_to_set=None
            lowest_entropy=len(all_structure_set)
            collapsed_count = 0
            for position in arena:
                possibilities = arena[position]

                entropy = log2(len(possibilities))

                if entropy==0:
                    collapsed_count+=1
                else:
                    if entropy<lowest_entropy:
                        position_to_set=position
                        lowest_entropy=entropy
            
            bar(collapsed_count/termination_count)

            if(position_to_set==None or collapsed_count>=termination_count):
                print("eyyyy solved")
                break
                    
            possibilities=list(arena[position_to_set])
            while True:
                if len(possibilities)==0:
                    # if nothing can be used, rewind the changes made from the last step
                    to_roll_back = change_record.pop()
                    for key in to_roll_back:
                        arena[key].update(to_roll_back[key])
                    
                    # remove the step since it wouldn't work in this situation
                    roll_back_position,roll_back_selection = step_record.pop()
                    arena[roll_back_position].remove(roll_back_selection)

                    print(f"roll back {roll_back_position}")
                    break


                # select a possibility
                choosen_possibility=choice(possibilities)

                # remove the possibility from current iteration
                possibilities.remove(choosen_possibility)
                
                # record the change for rewinding
                if not position_to_set in change_record[-1]:
                    change_record[-1][position_to_set]=set()
                change_record[-1][position_to_set].add(choosen_possibility)

                # propagate the effect of this change out
                (suc,change)=propagate(arena,extended_constraints,all_structure_set,position_to_set,choosen_possibility)

                if suc:
                    # when it is rewind past this point, this possibility doessn't work and would need to be removed
                    # so record it for whent that time comes
                    step_record.append((position_to_set,choosen_possibility))
                    # the selected possibility does work, at least for this step
                    # save enough information for rewind
                    change_record.append(change)
                    # saveDebugArena(arena)
                    break
                else:
                    # this possibility doesn't work in this situation, remove it
                    arena[position_to_set].remove(choosen_possibility)
                    # the selected possibility doesn't work out, rewind and try other possibilities
                    # rewind should have been done inside of propagate
                    continue

    return arena
