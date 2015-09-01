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
	@property
	def layers(self):
		layers = defaultdict(set)
		for target, node in self.graph.items():
			layers[c_type(target)].add(target)
		return layers
	@property
	def inputs_to_targets(self):
		i2t = defaultdict(set)
		for target, node in self.graph.items():
			for input in node.inputs:
				i2t[input].add(target)
		return i2t

# ------------------------------------------------------------------------------
# classic C/C++ build tree is defined as
# workspace containing projects, project can depend on other projects
# each project have C/C++ -> obj -> exe/lib flow
# with global compiling and linking options
# optionally each file can have specific compiling options
# each project also have pre and post build steps

class BuildTreeC:
	def __init__(self, build_graph, end_targets, ir_reader):
		self.workspace_graph = BuildGraphC(build_graph.graph)
		self.end_targets = end_targets
		self.ir_reader = ir_reader

		# extract all normal projects
		self.workspace_links = self.workspace_graph.layers["links"]
		#self.workspace_inputs_map = self.workspace_graph.inputs_to_targets
		self.projects_graphs = {target: self.ir_reader.build_graph(target, self.workspace_links) for target in self.workspace_links}

		# some targets can be based on projects links, we move all of them to separate project
		self.workspace_postbuild_targets = set(self.end_targets).difference(self.workspace_links)
		if len(self.workspace_postbuild_targets):
			self.workspace_postbuild_graph = self.ir_reader.build_graph(self.workspace_postbuild_targets, self.workspace_links)
		else:
			self.workspace_postbuild_graph = None

		pprint(self.workspace_postbuild_graph)

		#pprint(self.workspace_links)
		#pprint(self.projects_graphs)
		#pprint(self.workspace_postbuild)
		#pprint(inputs_to_targets)
		#pprint(layers)

		#pprint(build_graph)

	#def graph(self, target):
	#	return self.ir_reader.build_graph(target)




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
