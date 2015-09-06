# DAG -> c/cpp build tree

# TODO some ideas :
# - it's possible to pass DAG which only executes huge shell script, like :
#
#   rule foo
#     command = cl -c test.cpp /Fo:test.obj $
#               cl test.obj /link /out:test.exe
#   build bar:foo baz
#
#   in this case DAG doesn't mean sense, but builds commands do
#   should we rebuild DAG from shell script then ?
#
# - C and CXX flags should be different !

import os
import shlex
from collections import defaultdict
from collections import namedtuple
from lib.mask_irreader import BuildGraph, IRreader

# ------------------------------------------------------------------------------
# conversion from file extension to semantic type

c_ext_types = {
	"sources": [".c", ".cpp", ".cxx", ".cc"],
	"headers": [".h", ".hpp", ".hxx"],
	"objs": [".obj"],
	"links": [".exe", ".lib", ".dll", ".a"]
}

c_ext_inv_types = {ext: type for type, list in c_ext_types.items() for ext in list}

# TODO how it works with unix executables ? they don't have extension
def c_type(target):
	return c_ext_inv_types.get(os.path.splitext(target)[1], "unknown")

# ------------------------------------------------------------------------------
# command line tools

class CommandArgsCL(namedtuple("CommandArgsCL", ["command", "tool", "inputs",
	"outputs", "args", "link", "link_args", "link_inputs", "link_outputs"])):
	__slots__ = ()
	def __new__(self, argv):
		obj = super(self, CommandArgsCL).__new__(self, argv, argv[0], [], [],
			set(), False, set(), [], [])

		# parse arguments for CL
		for arg in argv[1:]:
			if arg.startswith("/") or arg.startswith("-"):
				arg = "/" + arg[1:]
				if arg == "/link":
					obj = obj._replace(link = True) # WTF python
					continue
				elif obj.link == False and arg.startswith("/Fo"):
					obj.outputs.append(arg[3:])
				elif obj.link == True and arg.startswith("/out:"):
					obj.link_outputs.append(arg[5:])
				elif obj.link == False:
					obj.args.add(arg)
				else:
					obj.link_args.add(arg)
			else:
				if arg.startswith("@"):
					print("TODO rspfiles are not supported yet")
				if obj.link == False:
					obj.inputs.append(arg)
				else:
					obj.link_inputs.append(arg)
		return obj

	@property
	def is_compiling(self):
		return not self.link # not really sure

	@property
	def is_linking(self):
		return self.link

# TODO fill this up
know_commands = {
	"cl": CommandArgsCL
}

# TODO fill this up
toolsets = {
	"msvc": set(["cl", "link", "lib"]),
	"gcc": set(["gcc", "g++"])
}
tool_to_toolset = {tool: toolset for toolset, list in toolsets.items() for tool in list}


def parse_command(command):
	argv = shlex.split(command)
	program = argv[0]
	if program not in know_commands:
		print("unknown program %s" % program)
		return None
	return know_commands.get(argv[0])(argv)


# ------------------------------------------------------------------------------
# build graph with C tree properties
class BuildGraphC(BuildGraph):
	__slots__ = ()
	def __new__(self, build_graph, targets, sln_links, ir_reader):
		obj = super(self, BuildGraphC).__new__(self, build_graph.graph)
		obj.sln_links = sln_links
		if type(targets) is str:
			obj.targets = set([targets])
		else:
			obj.targets = targets
		obj.ir_reader = ir_reader

		obj.prebuilds = set()			# prebuild targets
		obj.postbuilds = set()			# postbuild targets
		obj.toolset = ""				# toolset name
		obj.common_args = set()
		obj.common_link_args = set()
		obj.to_be_compiled = {}			# files for compiler, key - name, val - additional compiler args
		obj.to_be_linked = {}			# files for linker (libs/objs), key - name, val - additional linker args
		obj.all_sourceish_files = set()	# files that should be visible in IDE

		return obj

	# constructs graph from targets, links and ir reader
	@classmethod
	def construct(self, targets, sln_links, ir_reader):
		return BuildGraphC(ir_reader.build_graph(targets, sln_links), targets, sln_links, ir_reader)

	# return build layers defined in c_ext_types
	@property
	def layers(self):
		layers = defaultdict(set)
		for target, node in self.graph.items():
			layers[c_type(target)].add(target)
		return layers

	# return inputs dictionary mapped to target(s)
	@property
	def inputs_to_targets(self):
		i2t = defaultdict(set)
		for target, node in self.graph.items():
			for input in node.inputs:
				i2t[input].add(target)
		return i2t

	# return dependencies of this graph
	@property
	def deps(self):
		return set(self.inputs_to_targets.keys()).intersection(self.sln_links)

	# this tree supposed to be normal C build tree
	# in this case all targets are from link stage (see BuildTreeC)
	# so there is no post build step ...
	def analyse(self):
		# basic values
		layers = self.layers
		links = layers["links"]
		sources = layers["sources"]
		objs = layers["objs"]
		headers = layers["headers"]
		unknowns = layers["unknown"]
		sources_and_headers = sources.union(headers)
		def remove_from_lists(target): # TODO clean up this crap
			if target in links:
				links.remove(target)
			if target in sources:
				sources.remove(target)
			if target in objs:
				objs.remove(target)
			if target in headers:
				headers.remove(target)
			if target in unknowns:
				unknowns.remove(target)
			if target in sources_and_headers:
				sources_and_headers.remove(target)

		# sanity check
		if len(links.difference(self.targets)) > 0:
			print("Warning ! list of targets from layers is different from external list of targets : %s vs %s" % (str(links), str(self.targets)))

		# prebuilds set
		prebuilds = set()
		def add_to_prebuild(target):
			prebuilds.add(target)
			remove_from_lists(target)
			for input in self.graph[target].inputs:
				add_to_prebuild(input)

		# check that all targets are built by one build command
		# TODO how this will work when .lib file is defined as phony to target to .dll ?
		all_link_indexes = set([self.graph[target].index for target in links])
		build_link = self.ir_reader.build_commands(all_link_indexes)
		if len(all_link_indexes) > 1:
			print("Warning ! Multiple build commands create required project targets :")
			print(build_link)

		# let's move all unknowns and all their inputs to prebuilds
		# this will move to prebuild all source files\obj\links that are inputs of unknowns
		for target in unknowns.copy():
			add_to_prebuild(target)

		# sanity check
		if len(links) == 0:
			print("Warning ! unknowns' dependencies moved all linked files to prebuild step, so we have nothing to build")

		# sanity checks on dependency order
		# TODO potentially we can move incorrect targets to prebuilds
		for target in sources_and_headers:
			if target in objs:
				print("Warning ! source target depends on obj input ! (%s)" % target)
			if target in links:
				print("Warning ! source target depends on link input ! (%s)" % target)
		for target in objs:
			if target in links:
				print("Warning ! obj target depends on link input ! (%s)" % target)

		# on this stage we have :
		# - all left links depend on objs/sources/headers/prebuold
		# - all left objs depend on sources/headers/prebuild
		# - all left sources/headers depend on prebuild

		# let's move all sources and headers to prebuild
		# because build tree only can build objs and links
		for target in sources_and_headers.copy():
			add_to_prebuild(target)

		# now it's time for actual builds analysis

		# let's start with parsing build commands list
		def parse_builds(builds):
			out = []
			for build in builds:
				cmd = self.ir_reader.ir.evaluate(build, "command")
				parsed_cmd = parse_command(cmd)
				out.append(parsed_cmd)
			return out
		build_exclusions = prebuilds.union(self.deps)
		links_and_objs = links.union(objs)
		cmds = parse_builds(self.ir_reader.build_commands(links_and_objs, build_exclusions))

		# figure out toolset and common compiler and linker args
		toolset = None
		common_args = None
		common_link_args = None
		for cmd in cmds:
			if cmd.tool not in tool_to_toolset:
				print("Warning ! unknown tool " + cmd.tool)
			cmd_toolset = tool_to_toolset.get(cmd.tool)

			if not toolset:
				toolset = cmd_toolset
			elif toolset != cmd_toolset:
				print("Warning ! toolset differs between cmd's : %s vs %s" % (toolset, cmd_toolset))

			if cmd.is_compiling:
				if len(cmd.link_args):
					print("Warning ! linking args are present in compiling command " + str(cmd))
				if len(cmd.link_outputs):
					print("Warning ! compiling command produce linked outputs " + str(cmd))
				if not common_args:
					common_args = cmd.args
				else:
					common_args = common_args.intersection(cmd.args)
			elif cmd.is_linking:
				if len(cmd.args):
					print("Warning ! compiling args are present in linking command " + str(cmd))
				if len(cmd.outputs):
					print("Warning ! linking command produce compiled outputs " + str(cmd))
				if not common_link_args:
					common_link_args = cmd.link_args
				else:
					common_link_args = common_link_args.intersection(cmd.link_args)
			else:
				print("Warning ! unknown cmd action " + str(cmd))

		# key is file name, value is custom arguments
		to_be_compiled = {}
		to_be_linked = {}

		# sets of produced targets, just for sanity check that we cover everything
		compiled_targets = set()
		linked_targets = set()

		for cmd in cmds:
			if cmd.is_compiling:
				for input in cmd.inputs:
					if input in to_be_compiled:
						print("Warning ! two or more commands compile %s" % input)
					args = common_args.difference(cmd.args)
					to_be_compiled[input] = args
				compiled_targets = compiled_targets.union(set(cmd.outputs))
			elif cmd.is_linking:
				for input in cmd.link_inputs + cmd.inputs:
					if input in to_be_linked:
						print("Warning ! two or more commands link %s" % input)
					args = common_link_args.difference(cmd.link_args)
					to_be_linked[input] = args
				linked_targets = linked_targets.union(set(cmd.link_outputs))

		# let's sanitize prebuilds list to exclude already built targets
		for target in prebuilds.copy():
			if not self.graph[target].index:
				prebuilds.remove(target)

		# looks like we are done
		self.prebuilds = prebuilds
		self.postbuilds = set()
		self.toolset = toolset
		self.common_args = common_args
		self.common_link_args = common_link_args
		self.to_be_compiled = to_be_compiled
		self.to_be_linked = to_be_linked
		self.all_sourceish_files = layers["sources"].union(layers["headers"]).union(layers["unknown"])

	# this tree only have postbuild step
	def analyse_postbuild(self):
		postbuilds = set()
		for target in self.graph.keys():
			if self.graph[target].index:
				postbuilds.add(target)
		self.postbuilds = postbuilds

# ------------------------------------------------------------------------------
# classic C/C++ build tree is defined as
# solution containing projects, project can depend on other projects
# each project have C/C++ -> obj -> exe/lib flow
# with global compiling and linking options
# optionally each file can have specific compiling options
# each project also have pre and post build steps

class BuildTreeC:
	def __init__(self, build_graph, end_targets, ir_reader):
		self.sln_graph = BuildGraphC(build_graph, end_targets, set(), ir_reader)
		self.end_targets = end_targets
		self.ir_reader = ir_reader

		# extract all normal projects
		self.sln_links = self.sln_graph.layers["links"]
		self.prjs_graphs = {
			target: BuildGraphC.construct(target, self.sln_links, self.ir_reader)
			for target in self.sln_links
		}

		# some targets can be based on projects links, we move all of them to separate project
		self.sln_postbuild_targets = set(self.end_targets).difference(self.sln_links)
		if len(self.sln_postbuild_targets):
			self.sln_postbuild_graph = BuildGraphC.construct(self.sln_postbuild_targets, self.sln_links, self.ir_reader)
		else:
			self.sln_postbuild_graph = None

		# figure out pre and post build steps
		for prj in self.prjs_graphs.values():
			prj.analyse()
		if self.sln_postbuild_graph:
			self.sln_postbuild_graph.analyse_postbuild()

# ------------------------------------------------------------------------------

def to_tree(ir, args = None):
	ir_reader = IRreader(ir)

	variation = None
	if args:
		variation = args.get("variation")
	end_targets = ir_reader.end_targets(variation)
	graph = ir_reader.build_graph(end_targets)

	return BuildTreeC(graph, end_targets, ir_reader)