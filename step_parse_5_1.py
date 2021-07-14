# HR 19/08/2019 to 10/12/2019
# Added all extra code I've done up to this point

# TH: I am using this to turn the script into a module file to make it useable else where
# We can add functionally as new things are made.

# HR July 2019
# To parse STEP file

# Regular expression module
import re

# For powerset construction
from itertools import chain, combinations

def powerset(iterable):
    "powerset([1,2,3]) --> () (1,) (2,) (3,) (1,2) (1,3) (2,3) (1,2,3)"
    s = list(iterable)
    return chain.from_iterable(combinations(s, r) for r in range(len(s)+1))

# Import networkx for plotting lattice
import networkx as nx

# Random number generator
#from random import randrange

# TH: Import treelib for drawing a tree stucture
# pip install --upgrade ete3
#from treelib import Node
from treelib import Tree

# Import "anytree" as well as "treelib" as better rendering capabilities
#from anytree import AnyNode, Node, RenderTree

#TH: useful for working with files
import os

import sys

#TH: for exporting to json format
import json

# HR Oct 19
# Allow stdout to be captured for later use
from io import StringIO



class Capture(list):

    # Class for capturing stdout
    def __enter__(self):
        self._stdout = sys.stdout
        sys.stdout = self._stringio = StringIO()
        return self

    def __exit__(self, *args):
        self.extend(self._stringio.getvalue().splitlines())
        del self._stringio
        sys.stdout = self._stdout



class StepParse:

    def __init__(self):
        pass

    def load_step(self,step_filename):

        self.nauo_lines          = []
        self.prod_def_lines      = []
        self.prod_def_form_lines = []
        self.prod_lines          = []
        self.filename = os.path.splitext(step_filename)[0]



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
                            self.nauo_lines.append(line_hold)
                        elif line_type == 'prod_def':
                            self.prod_def_lines.append(line_hold)
                        elif line_type == 'prod_def_form':
                            self.prod_def_form_lines.append(line_hold)
                        elif line_type == 'prod':
                            self.prod_lines.append(line_hold)
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
                                self.nauo_lines.append(line_hold)
                            elif line_type == 'prod_def':
                                self.prod_def_lines.append(line_hold)
                            elif line_type == 'prod_def_form':
                                self.prod_def_form_lines.append(line_hold)
                            elif line_type == 'prod':
                                self.prod_lines.append(line_hold)
                            line_hold = ''
                            line_type = ''
                    else:
                        #TH: if not end of file
                        line_hold = line_hold + line.rstrip()



        self.nauo_refs          = []
        self.prod_def_refs      = []
        self.prod_def_form_refs = []
        self.prod_refs          = []

        # TH: added 'replace(","," ").' to replace ',' with a space to make the spilt easier if there are not spaces inbetween the words'
        # Find all (# hashed) line references and product names
        # TH: it might be worth finding a different way of extracting data we do want rather than fixes to get rid of the data we don't
        for j,el_ in enumerate(self.nauo_lines):
            self.nauo_refs.append([el.rstrip(',')          for el in el_.replace(","," ").replace("="," ").split()                  if el.startswith('#')])
        for j,el_ in enumerate(self.prod_def_lines):
            self.prod_def_refs.append([el.rstrip(',')      for el in el_.replace(","," ").replace("="," ").split()                  if el.startswith('#')])
        for j,el_ in enumerate(self.prod_def_form_lines):
            self.prod_def_form_refs.append([el.rstrip(',') for el in el_.replace(","," ").replace("="," ").split()                  if el.startswith('#')])
        for j,el_ in enumerate(self.prod_lines):
            self.prod_refs.append([el.strip(',')           for el in el_.replace(","," ").replace("("," ").replace("="," ").split() if el.startswith('#')])
            self.prod_refs[j].append(el_.split("'")[1])

        # Get first two items in each sublist (as third is shape ref)
        #
        # First item is 'PRODUCT_DEFINITION' ref
        # Second item is 'PRODUCT_DEFINITION_FORMATION <etc>' ref
        self.prod_all_refs = [el[:2] for el in self.prod_def_refs]

        # Match up all references down to level of product name
        for j,el_ in enumerate(self.prod_all_refs):

            # Add 'PRODUCT_DEFINITION' ref
            for i,el in enumerate(self.prod_def_form_refs):
                if el[0] == el_[1]:
                    el_.append(el[1])
                    break

            # Add names from 'PRODUCT_DEFINITION' lines
            for i,el in enumerate(self.prod_refs):
                if el[0] == el_[2]:
                    el_.append(el[2])
                    break



        # Find all parent and child relationships (3rd and 2nd item in each sublist)
        self.parent_refs = [el[1] for el in self.nauo_refs]
        self.child_refs  = [el[2] for el in self.nauo_refs]

        # Find distinct parts and assemblies via set operations; returns list, so no repetition of items
        self.all_type_refs  = set(self.child_refs) | set(self.parent_refs)
        self.ass_type_refs  = set(self.parent_refs)
        self.part_type_refs = set(self.child_refs) - set(self.parent_refs)
        #TH: find root node
        self.root_type_refs = set(self.parent_refs) - set(self.child_refs)

        # Create simple parts dictionary (ref + label)
        self.part_dict     = {el[0]:el[3] for el in self.prod_all_refs}
#        self.part_dict_inv = {el[3]:el[0] for el in self.prod_all_refs}



    def show_values(self):
        # TH: basic testing, if needed these could be spilt up
        print(self.nauo_lines)
        print(self.prod_def_lines)
        print(self.prod_def_form_lines)
        print(self.prod_lines)
        print(self.nauo_refs)
        print(self.prod_def_refs)
        print(self.prod_def_form_refs)
        print(self.prod_refs)


#    HR: "create_dict" replaced by list comprehension elsewhere
#
#    def create_dict(self):
#
#        # TH: links nauo number with a name and creates dict
#        self.part_dict  = {}
#        for part in self.all_type_refs:
#            for sublist in self.prod_def_refs:
#                if sublist[0] == part:
#                    prod_loc = '#' + re.findall('\d+',sublist[1])[0]
#                    pass
#            for sublist in self.prod_def_form_refs:
#                if sublist[0] == prod_loc:
#                    prod_loc = '#' + str(re.findall('\d+',sublist[1])[0])
#                    pass
#            for sublist in self.prod_refs:
#                if sublist[0] == prod_loc:
#                    part_name = sublist[2]
#
#            self.part_dict[part] = part_name



    def create_tree(self):

        #TH: create tree diagram in newick format
        #TH: find root node

        self.tree = Tree()
        #TH: check if there are any parts to make a tree from, if not don't bother
        if self.part_dict == {}:
            return

        root_node_ref = list(self.root_type_refs)[0]
        # HR added part reference as data for later use
        self.tree.create_node(self.part_dict[ root_node_ref ] , 0, data = {'ref': root_node_ref})

        #TH: created root node now fill in next layer
        #TH: create dict for tree, as each node needs a unique name
        i = [0] # Iterates through nodes
        self.tree_dict = {}
        self.tree_dict[i[0]] = root_node_ref

        def tree_next_layer(self,parent):
            root_node = self.tree_dict[i[0]]
            for line in self.nauo_refs:
                if line[1] == root_node:
                    i[0] += 1
                    self.tree_dict[i[0]] = str(line[2])
                    # HR added part reference as data for later use
                    self.tree.create_node( self.part_dict[line[2]], i[0] , parent=parent, data = {'ref': str(line[2])})
                    tree_next_layer(self,i[0])

        tree_next_layer(self,0)
        self.appended = False

        self.get_levels()



    def get_levels(self):

        # Initialise dict and get first level (leaves)
        self.levels = {}
        self.levels_set_p = set()
        self.levels_set_a = set()
        self.leaf_ids = [el.identifier for el in self.tree.leaves()]

        def do_level(self, tree_level):
            # Get all nodes within this level
            node_ids = [el for el in self.tree.nodes if self.tree.level(el) == tree_level]
            for el in node_ids:
                # If leaf, then n_p = 1 and n_a = 1
                if el in self.leaf_ids:
                    self.levels[el] = {}
                    self.levels[el]['n_p'] = 1
                    self.levels[el]['n_a'] = 1
                # If assembly, then get all children and sum all parts + assemblies
                else:
                    # Get all children of node and sum levels
                    child_ids = self.tree.is_branch(el)
                    child_sum_p = 0
                    child_sum_a = 0
                    for el_ in child_ids:
                        child_sum_p += self.levels[el_]['n_p']
                        child_sum_a += self.levels[el_]['n_a']
                    self.levels[el] = {}
                    self.levels[el]['n_p'] = child_sum_p
                    self.levels[el]['n_a'] = child_sum_a + 1
                    self.levels_set_p.add(child_sum_p)
                    self.levels_set_a.add(child_sum_a + 1)

        # Go up through tree levels and populate lattice level dict
        for i in range(self.tree.depth(),-1,-1):
            do_level(self, i)

        self.create_lattice()



    def create_lattice(self):

        # Create lattice
        self.g = nx.DiGraph()
        self.default_colour = 'r'
        # Get root node and set parent to -1 to maintain data type of "parent"
        # Set position to top/middle
        node_id    = self.tree.root
        label_text = self.tree.get_node(node_id).tag
        self.g.add_node(node_id, parent = -1, label = label_text, colour = self.default_colour)

        # Do nodes from treelib "nodes" dictionary
        for key in self.tree.nodes:
            # Exclude root
            if key != self.tree.root:
                parent_id  = self.tree.parent(key).identifier
                label_text = self.tree.get_node(key).tag
                # Node IDs same as for tree
                self.g.add_node(key, parent = parent_id, label = label_text, colour = self.default_colour)

        # Do edges from nodes
        for key in self.tree.nodes:
            # Exclude root
            if key != self.tree.root:
                parent_id = self.tree.parent(key).identifier
                self.g.add_edge(key, parent_id)

        # Get set of parents of leaf nodes
        leaf_parents = set([self.tree.parent(el).identifier for el in self.leaf_ids])

        # For each leaf_parent, set position of leaf nodes sequentially
        i = 0
        no_leaves = len(self.tree.leaves())
        for el in leaf_parents:
            for el_ in self.tree.is_branch(el):
                child_ids = [el.identifier for el in self.tree.leaves()]
                if el_ in child_ids:
                    self.g.nodes[el_]['pos'] = ((i/(no_leaves-1)),1)
                    i += 1

        # To set plot positions of nodes from lattice levels
        #
        # Traverse upwards from leaves
        for el in sorted(list(self.levels_set_a)):
            # Get all nodes at that level
            node_ids = [k for k,v in self.levels.items() if v['n_a'] == el]
            # Get all positions of children of that node
            # and set position as mean value of them
            for el_ in node_ids:
                child_ids = self.tree.is_branch(el_)
                pos_sum = 0
                for el__ in child_ids:
                    pos_    = self.g.nodes[el__]['pos'][0]
                    pos_sum += pos_
                pos_sum = pos_sum/len(child_ids)
                self.g.nodes[el_]['pos'] = (pos_sum, el)

        

#    def append_labels(self):
#
#        # Append node IDs from treelib to node labels, as ctc only supports text labels
#        if self.appended == False:
#            separator = "-"
#            for i in range(self.tree.size()):
#                newtag = self.tree.get_node(i).tag + separator + str(i)
#                self.tree.update_node(i, tag = newtag)
#        else:
#            print("Tree data already appended")



    def print_tree(self):

        try:
            self.tree.show()
        except:
            self.create_tree()
            self.tree.show()



    def tree_to_json(self,save_to_file=False,filename='file',path=''):

        #TH: return json format tree, can also save to file
        if self.tree.size() != 0:
            data = self.tree.to_json()
            j = json.loads(data)
            if save_to_file==True:
                if path:
                    file_path = os.path.join(path,filename)
                else:
                    file_path = filename

                with open(file_path + '.json', 'w') as outfile:
                    json.dump(j, outfile)

            return data
        else:
            print("no tree to print")
            return
