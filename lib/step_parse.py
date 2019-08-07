# TH: I am using this to turn the script into a module file to make it useable else where
# We can add functionally as new things are made.

# HR July 2019
# To parse STEP file

# Regular expression module
import re
# Interator for tallying contents of list, etc.
from collections import Counter
# TH: Import treelib for drawing a tree stucture
# pip install --upgrade ete3
from treelib import Node, Tree
#TH: useful for working with files
import os
#TH: for exporting to json format
import json

# Various iterator/generator tools
#import itertools


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
		for j in range(len(self.nauo_lines)):
			self.nauo_refs.append([el.rstrip(',')          for el in self.nauo_lines[j].replace(","," ").split()          if el.startswith('#')])
		for j in range(len(self.prod_def_lines)):
			self.prod_def_refs.append([el.rstrip(',')      for el in self.prod_def_lines[j].replace(","," ").split()      if el.startswith('#')])
		for j in range(len(self.prod_def_form_lines)):
			self.prod_def_form_refs.append([el.rstrip(',') for el in self.prod_def_form_lines[j].replace(","," ").split() if el.startswith('#')])
		for j in range(len(self.prod_lines)):
			self.prod_refs.append([el.strip(',')           for el in self.prod_lines[j].replace(","," ").replace("("," ").split()          if el.startswith('#')])
			self.prod_refs[j].append(self.prod_lines[j].split("'")[1])


		# Get first two items in each sublist (as third is shape ref)
		#
		# First item is 'PRODUCT_DEFINITION' ref
		# Second item is 'PRODUCT_DEFINITION_FORMATION <etc>' ref
		self.prod_all_refs = [el[:2] for el in self.prod_def_refs]

		# Match up all references down to level of product name
		for j in range(len(self.prod_all_refs)):
			
			# Add 'PRODUCT_DEFINITION' ref
			for i in range(len(self.prod_def_form_refs)):
				if self.prod_def_form_refs[i][0] == self.prod_all_refs[j][1]:
					self.prod_all_refs[j].append(self.prod_def_form_refs[i][1])
					break
			
			# Add names from 'PRODUCT_DEFINITION' lines
			for i in range(len(self.prod_refs)):
				if self.prod_refs[i][0] == self.prod_all_refs[j][2]:
					self.prod_all_refs[j].append(self.prod_refs[i][2])
					break



		# Find all parent and child relationships (3rd and 2nd item in each sublist)
		self.parent_refs = [el[1] for el in self.nauo_refs]
		self.child_refs  = [el[2] for el in self.nauo_refs]

		# Find distinct parts and assemblies via set operations; returns list, so no repetition of items
		self.all_type_refs  = set(self.child_refs) | set(self.parent_refs)
		self.ass_type_refs  = set(self.parent_refs)
		self.part_type_refs = set(self.child_refs) - set(self.parent_refs)




		# Get first two items in each sublist (as third is shape ref)
		#
		# First item is 'PRODUCT_DEFINITION' ref
		# Second item is 'PRODUCT_DEFINITION_FORMATION <etc>' ref
		self.prod_all_refs = [el[:2] for el in self.prod_def_refs]

		# Match up all references down to level of product name
		for j in range(len(self.prod_all_refs)):
			
			# Add 'PRODUCT_DEFINITION' ref
			for i in range(len(self.prod_def_form_refs)):
				if self.prod_def_form_refs[i][0] == self.prod_all_refs[j][1]:
					self.prod_all_refs[j].append(self.prod_def_form_refs[i][1])
					break
			
			# Add names from 'PRODUCT_DEFINITION' lines
			for i in range(len(self.prod_refs)):
				if self.prod_refs[i][0] == self.prod_all_refs[j][2]:
					self.prod_all_refs[j].append(self.prod_refs[i][2])
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
		self.create_dict()

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
		
	def create_dict(self):
		# TH: links nauo number with a name and creates dict
		self.part_dict  = {}
		for part in self.all_type_refs:
			for sublist in self.prod_def_refs:
				if sublist[0] == part:
					prod_loc = '#' + re.findall('\d+',sublist[1])[0]
					pass
			for sublist in self.prod_def_form_refs:
				if sublist[0] == prod_loc:
					prod_loc = '#' + str(re.findall('\d+',sublist[1])[0])
					pass
			for sublist in self.prod_refs:
				if sublist[0] == prod_loc:
					part_name = sublist[2]
					
			self.part_dict[part] = part_name
			
	def create_tree(self):
		#TH: create tree diagram in newick format 
		#TH: find root node
		
		self.tree = Tree()
		root_node_ref = list(self.root_type_refs)[0]
		self.tree.create_node(self.part_dict[ root_node_ref ] , 0)
		
		#TH: created root node now fill in next layer
		#TH: create dict for tree, as each node needs a unique name
		i = [0] # itirates through nodes
		self.tree_dict = {}
		self.tree_dict[i[0]] = root_node_ref
		def tree_next_layer(self,parent):
			root_node = self.tree_dict[i[0]]
			for line in self.nauo_refs:
				if line[1] == root_node:
					i[0] += 1
					self.tree_dict[i[0]] = str( line[2] )
					self.tree.create_node( self.part_dict[ line[2] ], i[0] , parent=parent)
					tree_next_layer(self,i[0])
		tree_next_layer(self,0) 
		
	def print_tree(self):
		try:
			self.tree.show()
		except:
			self.create_tree()
			self.tree.show()
			
	def tree_to_json(self,save_to_file=False,filename='file',path=''):
		#TH: return json format tree, can also save to file
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
		