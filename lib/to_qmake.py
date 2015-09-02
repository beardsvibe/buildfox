# mask ir to qmake exporter

import os
from pprint import pprint
from collections import defaultdict

from lib.tool_classic_tree import to_trees

from lib.mask_irreader import IRreader, BuildGraph

# ------------------------------------------------------------------------------
# conversion from file extension to semantic type

c_ext_types = {
	"sources": [".c", ".cpp", ".cxx", ".cc"],
	"headers": [".h", ".hpp", ".hxx"],
	"objs": [".obj"],
	"links": [".exe", ".lib", ".dll", ".a"]
}

c_ext_inv_types = {ext: type for type, list in c_ext_types.items() for ext in list}

def c_type(target):
	return c_ext_inv_types.get(os.path.splitext(target)[1], "unknown")

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
		sources = layers["sources"]
		objs = layers["objs"]
		headers = layers["headers"]
		unknowns = layers["unknowns"]
		sources_and_headers = sources.union(headers)

		# check that all targets are built by one build command
		# TODO how this will work when .lib file is defined as phony to target to .dll ?
		all_link_indexes = set([self.graph[target].index for target in self.targets])
		build_link = self.ir_reader.build_commands(all_link_indexes)
		if len(all_link_indexes) > 1:
			print("Warning ! Multiple build commands create required project targets :")
			print(build_link)

		# let's see if target depends on obj or source files
		prebuilds = set()
		for target in self.targets:
			for input in self.graph[target].inputs:
				if input in objs:
					# seem ok so far
					pass
				elif input in sources_and_headers:
					# this is rare case when compiler is called with source files and produce linked binary without obj files
					pass
				elif input in unknowns:
					prebuilds.add(input)
					pass

		pass

	# this tree only have postbuild step
	def analyse_postbuild(self):
		pass


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

		# dependencies
		#pprint({t: g.deps for t, g in self.prjs_graphs.items()})

		# figure out pre and post build steps
		for prj in self.prjs_graphs.values():
			prj.analyse()
		self.sln_postbuild_graph.analyse_postbuild()
		#pprint(self.prjs_graphs)




def to_string(ir, args = None):
	ir_reader = IRreader(ir)

	end_targets = ir_reader.end_targets(args.get("variation"))
	graph = ir_reader.build_graph(end_targets)

	t2 = BuildTreeC(graph, end_targets, ir_reader)
	#pprint(t)
	#pprint(t.graph[target])

	return ""
	trees = to_trees(ir)

	if len(trees) != 1:
		print("TODO : Warning ! only one project tree is supported in qmake generator now, and we got :")
		pprint(trees)

	tree = trees[0]

	output = "TEMPLATE = app\n"
	output += "SOURCES += " + " ".join([v.target.replace("\\", "/") for v in tree.source_targets]) + "\n"
	output += "QMAKE_CXXFLAGS = " + " ".join([v for v in tree.common_flags_compilation]) + "\n"
	output += "QMAKE_CFLAGS = $$QMAKE_CXXFLAGS\n"
	output += "QMAKE_LFLAGS = " + " ".join([v for v in tree.common_flags_link]) + "\n"
	
	output += """
# remove all built-in qmake compiler flags, because we tell qmake EXACTLY what to do
QMAKE_CXXFLAGS_RELEASE =
QMAKE_CXXFLAGS_DEBUG =
QMAKE_CXXFLAGS_MT =
QMAKE_CXXFLAGS_MT_DBG =
QMAKE_CXXFLAGS_MT_DLL =
QMAKE_CXXFLAGS_MT_DLLDBG =
QMAKE_CXXFLAGS_SHLIB =
QMAKE_CXXFLAGS_THREAD =
QMAKE_CXXFLAGS_WARN_OFF =
QMAKE_CXXFLAGS_WARN_ON =
QMAKE_CFLAGS_DEBUG =
QMAKE_CFLAGS_MT =
QMAKE_CFLAGS_MT_DBG =
QMAKE_CFLAGS_MT_DLL =
QMAKE_CFLAGS_MT_DLLDBG =
QMAKE_CFLAGS_RELEASE =
QMAKE_CFLAGS_SHLIB =
QMAKE_CFLAGS_THREAD =
QMAKE_CFLAGS_WARN_OFF =
QMAKE_CFLAGS_WARN_ON =
DEFINES =
CONFIG =
"""

	return output

def to_file(filename, ir, args = None):
	with open(filename, "w") as f:
		f.write(to_string(ir, args))
