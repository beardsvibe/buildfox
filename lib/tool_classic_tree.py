# build systems can be divided into two groups :
# * make-like, they can build any graph-like build manifest
# * msbuild-like, they only build predefined tree-like structures
# this utils are designed to convert first group manifest into second group

# TODO everything here is POC, so we need to make proper implementation later on

import os
import shutil
import shlex
from lib.tool_build_list import build_targets_dict, needed_to_execute_indexes, needed_to_execute_builds

# TODO
def is_source(name):
	return name.lower().endswith((".c", ".cpp", ".cxx", ".cc", ".h", ".hpp", ".hxx"))

# helper for msvc CL
class MSVCToolchainCL:
	def __init__(self):
		self.program = "" # executable name in shell, probably path + cl.exe
		self.args = set()
		self.files = []
		self.output_files = []
		self.link = False
		self.link_args = set()
		self.link_files = []
		self.link_output_files = []

	def parse_cmds(self, cmds):
		self.program = cmds[0]
		for arg in cmds[1:]:
			if arg.startswith("/") or arg.startswith("-"):
				arg = "/" + arg[1:]
				if arg == "/link":
					self.link = True
					continue
				elif self.link == False and arg.startswith("/Fo"):
					self.output_files.append(arg[3:])
				elif self.link == True and arg.startswith("/out:"):
					self.link_output_files.append(arg[4:])
				elif self.link == False:
					self.args.add(arg)
				else:
					self.link_args.add(arg)
			else:
				if arg.startswith("@"):
					print("TODO rspfiles are not supported yet")

				if self.link == False:
					self.files.append(arg)
				else:
					self.link_files.append(arg)

	def __repr__(self):
		out = ""
		out += "prog  : %s\n" % self.program
		out += "args  : %s\n" % " ".join(self.args)
		out += "files : %s\n" % " ".join(self.files)
		out += "outs  : %s\n" % " ".join(self.output_files)
		out += "link  : %s\n" % str(self.link)
		out += "largs : %s\n" % " ".join(self.link_args)
		out += "lfiles: %s\n" % " ".join(self.link_files)
		out += "louts : %s\n" % " ".join(self.link_output_files)
		return out

# helper for msvc cmd parsing
class MSVCToolchainCmd:
	def __init__(self):
		self.tool = None
		self.tool_name = ""

	def parse(self, command):
		cmds = shlex.split(command)
		self.tool_name = os.path.splitext(os.path.basename(cmds[0]))[0].lower()

		if self.tool_name == "cl":
			self.tool = MSVCToolchainCL()
			self.tool.parse_cmds(cmds)
		else:
			print("TODO unknown toolchain cmd : " + self.tool_name)

	def is_cl(self):
		return self.tool_name == "cl"

# simple helper for build target
class BuildTarget:
	def __init__(self, name, index, children):
		self.target = name
		self.build_index = index # number or None
		self.children = children # array of BuildTarget

	def is_exe_or_lib(self):
		return self.target.lower().endswith((".exe", ".lib", ".dll"))

	def is_obj(self):
		return self.target.lower().endswith(".obj")

	def is_source(self):
		return is_source(self.target)

	def __repr__(self):
		return self.target

# mask IR is not stricly a tree structure
# it's more like a graph (without cycles though)
# but msvc build structure is tree
# so this function convert ir graph to tree by cloning leafs
# all nodes on same level can be compiled in any order
def generate_generic_build_tree(target, readonly_ir, targets_dict):
	if target in targets_dict:
		index = targets_dict[target]
		children = []
		build = readonly_ir.builds[index]
		deps = set(build.inputs_explicit).union(build.inputs_implicit).union(build.inputs_order)
		for dep in deps:
			children.append(generate_generic_build_tree(dep, readonly_ir, targets_dict))
		return BuildTarget(target, index, children)
	else:
		return BuildTarget(target, None, [])

# abstraction for msvc build process :
# - prebuild step
# - compilation step (.cpp -> .obj)
# - linking step (.obj -> .exe)
# - postbuild step
class MSVCBuildTree:
	def __init__(self, prj_name, variation_name):
		self.prj_name = prj_name
		self.variation_name = variation_name
		self.objs_targets = [] # array of BuildTarget
		self.source_targets = [] # array of BuildTarget
		self.end_target = None # BuildTarget
		self.depends_on = [] # array of BuildTree
		self.pre_build = [] # array of BuildTarget
		self.post_build = [] # array of BuildTarget
		self.common_flags_compilation = set() # set of strings
		self.common_flags_link = set() # set of strings

	def __repr__(self):
		out = "buildtree :\n"
		out += "end target : %s\n" % self.end_target
		out += "objs targets : %s\n" % " ".join([str(v) for v in self.objs_targets])
		out += "src targets : %s\n" % " ".join([str(v) for v in self.source_targets])
		out += "depends on : %s\n" % " ".join([str(v) for v in self.depends_on])
		out += "common comp flags : %s\n" % " ".join(self.common_flags_compilation)
		out += "common link flags : %s\n" % " ".join(self.common_flags_link)
		return out

	def figure_out_compiler_settings(self, readonly_ir):
		compiler_rules = {}
		for obj_target in self.objs_targets:
			build = readonly_ir.builds[obj_target.build_index]
			rule = readonly_ir.rules[build.rule]
			if rule.name not in compiler_rules:
				compiler_rules[rule.name] = rule

		if len(compiler_rules.items()) > 1:
			print("TODO more then one compiler rule, custom arguments for compiling source files will be ignored for now")

		cl_calls = {}
		for rule_name, rule in compiler_rules.items():
			cmd = MSVCToolchainCmd()
			cmd.parse(rule.variables.get("command").value)
			if cmd.is_cl():
				cl_calls[rule_name] = cmd.tool
				if cmd.tool.link:
					print("TODO something is strange - cl is used for cpp -> obj flow, but link flag is set, it will be ignored")
			else:
				# TODO add this thing to prebuild
				print("TODO non cl compilers are not supported yet : " + cmd.tool_name)

		# intersection of all args sets is our common flags
		self.common_flags_compilation = set.intersection(*[cl.args for name, cl in cl_calls.items()])

	def figure_out_linker_settings(self, readonly_ir):
		build = readonly_ir.builds[self.end_target.build_index]
		link_rule = readonly_ir.rules.get(build.rule)

		cmd = MSVCToolchainCmd()
		cmd.parse(link_rule.variables.get("command").value)

		if cmd.is_cl():
			if not cmd.tool.link:
				raise ValueError("TODO something is strange - cl is used for obj -> exe/lib/dll flow, but link flag is NOT set")
			self.common_flags_link = cmd.tool.args
		else:
			# TODO add this thing to prebuild
			print("TODO non cl linkers are not supported yet : " + cmd.tool_name)

	def process_source(self, target):
		if len(target.children):
			# TODO add it as prebuild step
			print("TODO source depends on something, not supported now")
		self.source_targets.append(target)

	def process_object(self, target):
		if target.is_obj():
			# create new target that only depends on sources
			new_target = BuildTarget(target.target, target.build_index, []);
			for child in target.children:
				if child.is_source():
					new_target.children.append(child)
					self.process_source(child)
				else:
					self.pre_build.append(child)

			if len(new_target.children) == 0:
				print("TODO obj doesn't not have any direct source inputs : " + target.target)

			if len(new_target.children) > 1:
				print("TODO warning more then one source for obj target : " + target.target)

			# append it to objects
			self.objs_targets.append(new_target)
		elif target.is_source():
			print("TODO direct cpp -> exe compilation")
		else:
			self.pre_build.append(child)

	def restore_from_root(self, target):
		if target.is_exe_or_lib():
			self.end_target = target
			for child in self.end_target.children:
				self.process_object(child)
			self.end_target.children = []
		else:
			# we need to put this is empty project with pre/post build step
			print("TODO not possible to build (dep project) " + str(target))

def to_trees(readonly_ir):
	# get list of what we need to build
	targets_dict = build_targets_dict(readonly_ir)

	msvc_trees = []
	for prj_name, project in readonly_ir.projects.items():
		for variation_name, all_end_paths in project.variations.items():
			from pprint import pprint

			def order_trees(tree): # needed so depended on trees will come first
				for t in tree.depends_on:
					order_trees(t)
				msvc_trees.append(tree)

			for target in all_end_paths:
				generic_tree = generate_generic_build_tree(target, readonly_ir, targets_dict)
				build_tree = MSVCBuildTree(prj_name, variation_name)
				build_tree.restore_from_root(generic_tree)
				build_tree.figure_out_compiler_settings(readonly_ir)
				build_tree.figure_out_linker_settings(readonly_ir)
				order_trees(build_tree)

	return msvc_trees
