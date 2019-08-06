# HR July 2019
# To parse STEP file

# Regular expression module
import re

# Various iterator/generator tools
#import itertools

# Interator for tallying contents of list, etc.
from collections import Counter

# step_filename = 'E:/GrabCadData/Models/Step/Model00001.stp'

#step_filename = 'C:/Users/prctha/Python/pyocc2/as1-oc-214.stp'
step_filename = 'C:/Users/prctha/Desktop/Torch Assembly.STEP'


nauo_lines          = []
prod_def_lines      = []
prod_def_form_lines = []
prod_lines          = []

line_hold = ''
line_type = ''


# Find all search lines
with open(step_filename) as f:
    for line in f:
        # TH: read pointer of lines as they are read, so if the file has text wrap it will notice and add it to the following lines
        index = re.search("#(.*)=", line)
        if index:
            # TH: if not none then it is the start of a line so read it
            # want to hold line until it has checked next line
            # if next line is a new indexed line then save previous line
            if line_hold:
                if line_type == 'nauo':
                    nauo_lines.append(line_hold)
                elif line_type == 'prod_def':
                    prod_def_lines.append(line_hold)
                elif line_type == 'prod_def_form':
                    prod_def_form_lines.append(line_hold)
                elif line_type == 'prod':
                    prod_lines.append(line_hold)
                line_hold = ''
                line_type = ''
            
            
            prev_index = True  # TH rememeber previous line had an index
            if 'NEXT_ASSEMBLY_USAGE_OCCURRENCE' in line:
                line_hold = line.rstrip() 
                line_type = 'nauo'
            elif ('PRODUCT_DEFINITION ' in line or 'PRODUCT_DEFINITION(' in line):
                line_hold = line.rstrip() 
                line_type = 'prod_def'
            elif 'PRODUCT_DEFINITION_FORMATION' in line:
                line_hold = line.rstrip()
                line_type = 'prod_def_form'
            elif ('PRODUCT ' in line or 'PRODUCT(' in line):
                line_hold = line.rstrip() 
                line_type = 'prod'
        else:
            prev_index = False
            #TH: if end of file and previous line was held
            if 'ENDSEC;' in line:
                if line_hold:
                    if line_type == 'nauo':
                        nauo_lines.append(line_hold)
                    elif line_type == 'prod_def':
                        prod_def_lines.append(line_hold)
                    elif line_type == 'prod_def_form':
                        prod_def_form_lines.append(line_hold)
                    elif line_type == 'prod':
                        prod_lines.append(line_hold)
                    line_hold = ''
                    line_type = ''
            else:
                #TH: if not end of file
                line_hold = line_hold + line.rstrip()



nauo_refs          = []
prod_def_refs      = []
prod_def_form_refs = []
prod_refs          = []

# TH: added 'replace(","," ").' to replace ',' with a space to make the spilt easier if there are not spaces inbetween the words'

# Find all (# hashed) line references and product names
for j in range(len(nauo_lines)):
    nauo_refs.append([el.rstrip(',')          for el in nauo_lines[j].replace(","," ").split()          if el.startswith('#')])
for j in range(len(prod_def_lines)):
    prod_def_refs.append([el.rstrip(',')      for el in prod_def_lines[j].replace(","," ").split()      if el.startswith('#')])
for j in range(len(prod_def_form_lines)):
    prod_def_form_refs.append([el.rstrip(',') for el in prod_def_form_lines[j].replace(","," ").split() if el.startswith('#')])
for j in range(len(prod_lines)):
    prod_refs.append([el.strip(',')           for el in prod_lines[j].replace(","," ").split()          if el.startswith('#')])
    prod_refs[j].append(prod_lines[j].split("'")[1])


# Get first two items in each sublist (as third is shape ref)
#
# First item is 'PRODUCT_DEFINITION' ref
# Second item is 'PRODUCT_DEFINITION_FORMATION <etc>' ref
prod_all_refs = [el[:2] for el in prod_def_refs]

# Match up all references down to level of product name
for j in range(len(prod_all_refs)):
    
    # Add 'PRODUCT_DEFINITION' ref
    for i in range(len(prod_def_form_refs)):
        if prod_def_form_refs[i][0] == prod_all_refs[j][1]:
            prod_all_refs[j].append(prod_def_form_refs[i][1])
            break
    
    # Add names from 'PRODUCT_DEFINITION' lines
    for i in range(len(prod_refs)):
        if prod_refs[i][0] == prod_all_refs[j][2]:
            prod_all_refs[j].append(prod_refs[i][2])
            break



# Find all parent and child relationships (3rd and 2nd item in each sublist)
parent_refs = [el[1] for el in nauo_refs]
child_refs  = [el[2] for el in nauo_refs]

# Find distinct parts and assemblies via set operations; returns list, so no repetition of items
all_type_refs  = set(child_refs) | set(parent_refs)
ass_type_refs  = set(parent_refs)
part_type_refs = set(child_refs) - set(parent_refs)




# Get first two items in each sublist (as third is shape ref)
#
# First item is 'PRODUCT_DEFINITION' ref
# Second item is 'PRODUCT_DEFINITION_FORMATION <etc>' ref
prod_all_refs = [el[:2] for el in prod_def_refs]

# Match up all references down to level of product name
for j in range(len(prod_all_refs)):
    
    # Add 'PRODUCT_DEFINITION' ref
    for i in range(len(prod_def_form_refs)):
        if prod_def_form_refs[i][0] == prod_all_refs[j][1]:
            prod_all_refs[j].append(prod_def_form_refs[i][1])
            break
    
    # Add names from 'PRODUCT_DEFINITION' lines
    for i in range(len(prod_refs)):
        if prod_refs[i][0] == prod_all_refs[j][2]:
            prod_all_refs[j].append(prod_refs[i][2])
            break



# Find all parent and child relationships (3rd and 2nd item in each sublist)
parent_refs = [el[1] for el in nauo_refs]
child_refs  = [el[2] for el in nauo_refs]

# Find distinct parts and assemblies via set operations; returns list, so no repetition of items
all_type_refs  = set(child_refs) | set(parent_refs)
ass_type_refs  = set(parent_refs)
part_type_refs = set(child_refs) - set(parent_refs)



# CALCULATE LEVEL/DEGREE OF EACH NAUO, BOTTOM-UP
# SECTION NOT FINISHED 03/08/19
# NB Value ultimately corresponds to level of child
# No need for separate list of parents or children as each NAUO refers to a unique child
# because in this particular kind of graph, a child cannot have more than one parent 
#
# Append item to each P-C ref list to contain degree/level later
default_value = -1
[el.append(default_value) for el in nauo_refs]

# Set level of all NAUOs containing parts to 1
for el in nauo_refs:
    if el[2] in part_type_refs:
        el[3] = 1

# Do tally of P-Cs by parent refs for P-Cs containing parts as children
pc_tally = list(Counter([el[1] for el in nauo_refs if default_value not in el]).items())
# Make set of distinct tally values, as this determines degree/level of objects above
pc_set   = set([el[1] for el in pc_tally])

# Create list of tally values from set to impose ascending order
for el in list(pc_set):
    # Create list of all refs with this tally value, to loop over (if more than one instance)
    tally_list = []
    [tally_list.append(el_[0]) for el_ in pc_tally if el_[1] == el]
    print('Tally list ', el, ' = ', tally_list)
    # Go through tally values and assign part level to each NAUO
    for el_ in tally_list:
        for el__ in nauo_refs:
            if el__[2] == el_:
                el__[3] = el

# Cycle all NAUOs without parts as children
for el_ in [el for el in nauo_refs if el[2] not in part_type_refs]:
    pass

# Check that all P-C degree/levels are populated
for i in range(len(nauo_refs)):
    if default_value in nauo_refs[i]:
        print('NAUO degree values not fully populated')
        break



# CALCULATE LIST LEVEL OF EACH NAUO, BOTTOM-DOWN
# Append item to each P-C ref list to contain degree/level later
#[el.append(default_value) for el in nauo_refs]

# Initialise: Find top-level item and set list level to current length of "list_refs"
# i.e. 1 at top level and >1 and all lower level
list_refs = []
list_refs.append(list(set(parent_refs) - set(child_refs)))
[el.append(len(list_refs)) for el in nauo_refs if el[1] in list_refs[0]]

# Populate all subsequent levels
#
# Get all children of highest level populated so far




# Check that all P-C list levels are populated
for i in range(len(nauo_refs)):
    if default_value in nauo_refs[i]:
        print('NAUO list level values not fully populated')
        break

