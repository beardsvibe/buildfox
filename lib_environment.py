# BuildFox ninja generator

from lib_util import which

def discover():
	vars = {
		"variation": "debug"
	}

	if which("cl") and which("link") and which("lib"):
		vars["toolset_msvc"] = "true"

	if which("clang"):
		vars["toolset_clang"] = "true"

	if which("gcc") and which("g++"):
		vars["toolset_gcc"] = "true"

	if not which("ninja"):
		print("Warning ! Can't find ninja executable")

	if vars.get("toolset_msvc"):
		vars["toolset"] = "msvc"
	elif vars.get("toolset_clang"):
		vars["toolset"] = "clang"
	elif vars.get("toolset_gcc"):
		vars["toolset"] = "gcc"
	else:
		raise ValueError("Can't find any compiler")

	return vars
