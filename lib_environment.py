# BuildFox ninja generator

import shutil

def discover():
	vars = {
		"variation": "debug"
	}

	if shutil.which("cl") and shutil.which("link") and shutil.which("lib"):
		vars["toolset_msvc"] = "true"
	if shutil.which("clang"):
		vars["toolset_clang"] = "true"
	if shutil.which("gcc") and shutil.which("g++"):
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
