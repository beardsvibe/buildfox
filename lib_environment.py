# BuildFox ninja generator

from lib_util import which

def discover():
	vars = {
		"variation": "debug"
	}

	if which("cl.exe") and which("link.exe") and which("lib.exe"):
		vars["toolset_msvc"] = "true"

	if which("clang"):
		vars["toolset_clang"] = "true"

	if which("gcc") and which("g++"):
		vars["toolset_gcc"] = "true"

	if vars.get("toolset_msvc"):
		vars["toolset"] = "msvc"
	elif vars.get("toolset_clang"):
		vars["toolset"] = "clang"
	elif vars.get("toolset_gcc"):
		vars["toolset"] = "gcc"
	else:
		raise ValueError("cant find any compiler")

	return vars
