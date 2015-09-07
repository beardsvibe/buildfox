# mask ir to qmake exporter

import os
from pprint import pprint

from lib.buildtree_c import to_tree

def prj_to_string(prj_graph, name):
	target_to_template = {
		".exe": ("app", ""),
		".lib": ("lib", "staticlib"),
		".a": ("lib", "staticlib"),
		".dll": ("lib", "sharedlib")
	}

	template = set([target_to_template.get(os.path.splitext(target)[1]) for target in prj_graph.targets])
	if len(template) > 1:
		print("Warning ! multiple templates for prj " + str(template))
	if list(template)[0] == None:
		print("Warning ! unknown templates for prj ")
	for v in prj_graph.to_be_compiled.values():
		if len(v) > 0:
			print("Warning ! qmake doesn't support custom compilation flags for source files")
	for v in prj_graph.to_be_linked_objs.values():
		if len(v) > 0:
			print("Warning ! qmake doesn't support custom linkage flags for obj files")
	for v in prj_graph.to_be_linked_libs.values():
		if len(v) > 0:
			print("Warning ! qmake doesn't support custom linkage flags for lib files")

	# strip not required arguments
	args_lower = {arg.lower(): arg for arg in prj_graph.common_args}
	if "/showincludes" in args_lower:
		prj_graph.common_args.remove(args_lower.get("/showincludes"))

	output = "TEMPLATE = " + list(template)[0][0] + "\n"
	output += "QMAKE_PROJECT_NAME = " + name + "\n"
	output += "OBJECTS_DIR = objs_" + name + "\n"
	output += "MOC_DIR = $$OBJECTS_DIR\n"
	output += "CONFIG = " + list(template)[0][1] + "\n"
	output += "TARGET = " + os.path.splitext(list(prj_graph.targets)[0])[0].replace("\\", "/") + "\n"
	output += "SOURCES += " + " \\\n\t".join([v.replace("\\", "/") for v in sorted(prj_graph.to_be_compiled.keys())]) + "\n"
	output += "QMAKE_CXXFLAGS = " + " \\\n\t".join([v for v in sorted(prj_graph.common_args)]) + "\n"
	output += "QMAKE_CFLAGS = $$QMAKE_CXXFLAGS\n"
	output += "QMAKE_LFLAGS = " + " \\\n\t".join([v for v in sorted(prj_graph.common_link_args)]) + "\n"

	deps = prj_graph.deps
	if len(deps):
		output += "PRE_TARGETDEPS += " + " \\\n\t".join([v.replace("\\", "/") for v in sorted(deps)]) + "\n" # TODO not sure if this is correct
	all_libs = set(prj_graph.to_be_linked_libs.keys())
	if len(all_libs):
		for v in deps: # this one is really obscure, we need to link some libs before others, like ws2_32.lib
			all_libs.remove(v)
		output += "LIBS += " + " \\\n\t".join([v.replace("\\", "/") for v in sorted(all_libs)]) + "\n" # TODO not sure if this is correct
	if len(deps):
		output += "LIBS += " + " \\\n\t".join([v.replace("\\", "/") for v in sorted(deps)]) + "\n" # TODO not sure if this is correct

	if len(prj_graph.prebuilds):
		print("TODO qmake prebuilds")
	if len(prj_graph.postbuilds):
		print("TODO qmake postbuilds")
	# TODO
	#obj.prebuilds = set()			# prebuild targets
	#obj.postbuilds = set()			# postbuild targets
	#obj.toolset = ""				# toolset name

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
"""
	return output

def sln_to_string(tree, prjs):
	output = "TEMPLATE = subdirs\n"
	output += "SUBDIRS += " + " ".join(prjs.keys()) + "\n"
	for name, deps in prjs.items():
		output += name + ".file = " + name + ".pro\n"
		if len(deps):
			output += name + ".depends = " + " \\\n\t".join(deps) + "\n"

	# TODO add sln_postbuild_graph

	return output

def to_file(filename, ir, args = None):
	base_path = os.path.dirname(filename)
	tree = to_tree(ir, args)

	def prj_name(target):
		return "prj_" + target.replace(".", "_").replace("\\", "/").replace("/", "_")

	prjs = {}
	for targets, prj_graph in tree.prjs_graphs.items():
		name = prj_name(targets)
		prjs[name] = [prj_name(dep) for dep in prj_graph.deps]
		with open(os.path.join(base_path, name + ".pro"), "w") as f:
			f.write(prj_to_string(prj_graph, name))

	with open(filename, "w") as f:
		f.write(sln_to_string(tree, prjs))
