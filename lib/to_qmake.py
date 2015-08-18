from pprint import pprint
from lib.tool_classic_tree import to_trees

#from lib.mask_irreader import IRreader

def to_string(ir):
	#t = IRreader(ir)

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
		f.write(to_string(ir))
