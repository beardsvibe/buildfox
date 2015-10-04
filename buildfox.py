# BuildFox ninja generator

import os
import re
import copy
import argparse

from lib_engine import Engine
from lib_environment import discover

# ----------------------------------------------------------- fox core definitions

fox_core = r"""
# buildfox core configuration

# buildfox relies on scoped rules and they were added in ninja v1.6
ninja_required_version = 1.6

filter toolset:msvc
	# msvc support
	rule cxx
		command = cl $cxxflags /nologo /showIncludes -c $in /Fo$out
		description = cxx $in
		deps = msvc
		expand = true

	rule link
		command = cl /nologo @$out.rsp /link $ldflags /out:$out
		description = link $out
		rspfile = $out.rsp
		rspfile_content = $in

	rule link_dll
		command = cl /nologo @$out.rsp /link /DLL $ldflags /out:$out
		description = link $out
		rspfile = $out.rsp
		rspfile_content = $in

	rule lib
		command = lib $libflags @$out.rsp /nologo -OUT:$out
		description = lib $out
		rspfile = $out.rsp
		rspfile_content = $in

	auto *.obj: cxx r".*\.(cpp|cxx|c)$"
	auto *.exe: link r".*\.(obj|lib)$"
	auto *.dll: link_dll r".*\.(obj|lib)$"
	auto *.lib: lib r".*\.(obj|lib)$"

	cxxflags =
	ldflags =
	libflags =
	defines =
	includes =

	filter variation:debug
		cxxflags = /O1
	filter variation:release
		cxxflags = /Ox

	transformer defines: /D${param}
	transformer includes: /I${param}
"""

# ----------------------------------------------------------- main app

argsparser = argparse.ArgumentParser(description = "buildfox ninja generator")
argsparser.add_argument("-i", "--in", help = "input file", default = "build.fox")
argsparser.add_argument("-o", "--out", help = "output file", default = "build.ninja")
argsparser.add_argument("-w", "--workdir", help = "working directory")
argsparser.add_argument("variables", metavar = "name=value", type = str, nargs = "*", help = "variables with values to setup", default = [])
#argsparser.add_argument("-v", "--verbose", action = "store_true", help = "verbose output") # TODO
argsparser.add_argument("--no-core", action = "store_false",
	help = "disable parsing fox core definitions", default = True, dest = "core")
argsparser.add_argument("--no-env", action = "store_false",
	help = "disable environment discovery", default = True, dest = "env")
args = vars(argsparser.parse_args())

if args.get("workdir"):
	os.chdir(args.get("workdir"))

engine = Engine()

if args.get("env"):
	vars = discover()
	for name in sorted(vars.keys()):
		engine.on_assign((name, vars.get(name), "="))

for var in args.get("variables"):
	parts = var.split("=")
	if len(parts) == 2:
		name, value = parts[0], parts[1]
		engine.on_assign((name, value, "="))
	else:
		raise SyntaxError("unknown argument '%s'. you should use name=value syntax to setup a variable" % var)

if args.get("core"):
	engine.load_core(fox_core)

engine.load(args.get("in"))
engine.save(args.get("out"))
