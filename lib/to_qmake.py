# mask ir to qmake exporter

import os
from pprint import pprint
from collections import defaultdict

from lib.tool_classic_tree import to_trees

from lib.mask_irreader import IRreader

class BuildTreeC:
	def __init__(self, build_graph, root_target):
		self.ext_types = {
			"sources": [".c", ".cpp", ".cxx", ".cc"],
			"headers": [".h", ".hpp", ".hxx"],
			"objs": [".obj"],
			"links": [".exe", ".lib", ".dll", ".a"]
		}
		self.ext_inv_types = {ext: type for type, list in self.ext_types.items() for ext in list}
		self.build_graph = build_graph
		self.root_target = root_target

		for target in self.layers()["links"]:
			if target != root_target:
				print(target)
		#pprint(inputs_to_targets)
		#pprint(layers)

		#pprint(build_graph)

	def type(self, target):
		return self.ext_inv_types.get(os.path.splitext(target)[1], "unknown")

	def layers(self):
		layers = defaultdict(list)
		for target, node in self.build_graph.graph.items():
			layers[self.type(target)].append(target)
		return layers

	def inputs_to_targets(self):
		return {input: target for target, node in self.build_graph.graph.items() for input in node.inputs}


def to_string(ir, args = None):
	ir_reader = IRreader(ir)

	end_targets = ir_reader.end_targets(args.get("variation"))

	for target in end_targets:
		t = ir_reader.build_graph(target)
		
		t2 = BuildTreeC(t, target)
		
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
