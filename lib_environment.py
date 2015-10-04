# BuildFox ninja generator

import shutil

def discover():
	vars = {
		"variation": "debug"
	}

	if shutil.which("cl") and shutil.which("link") and shutil.which("lib"):
		vars["toolset_msvc"] = "true"
		vars["toolset_msvc_cl"] = "cl"
		vars["toolset_msvc_link"] = "link"
		vars["toolset_msvc_lib"] = "lib"

	if shutil.which("clang"):
		vars["toolset_clang"] = "true"
		vars["toolset_clang_clang"] = "clang"

	if shutil.which("gcc") and shutil.which("g++"):
		vars["toolset_gcc"] = "true"
		vars["toolset_gcc_gcc"] = "gcc"
		vars["toolset_gcc_g++"] = "g++"

	if vars.get("toolset_msvc"):
		vars["toolset"] = "msvc"
	elif vars.get("toolset_clang"):
		vars["toolset"] = "clang"
	elif vars.get("toolset_gcc"):
		vars["toolset"] = "gcc"
	else:
		raise ValueError("cant find any compiler")

	return vars
