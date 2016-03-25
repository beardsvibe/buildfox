#!/usr/bin/env python

# BuildFox ninja generator

import os
import re
import sys
import copy
import argparse
import subprocess

from lib_engine import Engine
from lib_environment import discover
from lib_selftest import selftest_setup, selftest_wipe
from lib_util import cxx_defines, cxx_includedirs
from lib_ide_vs import gen_vs
from lib_ide_xcode import gen_xcode
from lib_ide_make import gen_make
from lib_ide_cmake import gen_cmake
from lib_ide_qtcreator import gen_qtcreator
from lib_version import VERSION

# core definitions -----------------------------------------------------------

fox_core = r"""
# buildfox core configuration

# buildfox relies on deps and they were added in ninja v1.3
# please note, if you will use subfox/subninja commands
# then requirement will raise up to ninja v1.6 because we depend on scoped rules
ninja_required_version = 1.3

# some basic ignore folders
excluded_dirs = .git .hg .svn

filter toolset:msc
	# msc support
	cc = cl
	cxx = cl
	lib = lib

	rule cc
		command = $cc $cxxflags $defines $includedirs $disable_warnings /nologo /showIncludes -c $in /Fo$out
		description = cc $in
		deps = msvc
		expand = true

	rule cxx
		command = $cxx $cxxflags $defines $includedirs $disable_warnings /nologo /showIncludes -c $in /Fo$out
		description = cxx $in
		deps = msvc
		expand = true

	rule link
		command = $cxx /nologo @$out.rsp /link $ldflags $libdirs $ignore_default_libs /out:$out
		description = link $out
		rspfile = $out.rsp
		rspfile_content = $in $libs

	rule link_so
		command = $cxx /nologo @$out.rsp /link /DLL $ldflags $libdirs $ignore_default_libs /out:$out
		description = link $out
		rspfile = $out.rsp
		rspfile_content = $in $libs

	rule lib
		command = $lib $libflags @$out.rsp /nologo -OUT:$out
		description = lib $out
		rspfile = $out.rsp
		rspfile_content = $in $libs

	auto r"^(?i).*\.obj$": cxx r"^(?i).*\.(cpp|cxx|cc|c\+\+)$"
	auto r"^(?i).*\.obj$": cc r"^(?i).*\.c$"
	auto r"^(?i).*\.exe$": link r"^(?i).*\.obj$"
	auto r"^(?i).*\.dll$": link_so r"^(?i).*\.obj$"
	auto r"^(?i).*\.lib$": lib r"^(?i).*\.(obj|lib)$"

	# extensions transformers
	transformer application: ${param}.exe
	transformer objects: ${param}.obj
	transformer library: ${param}.lib
	transformer shared_library: ${param}.dll

	# MSC flags
	# more info here https://msdn.microsoft.com/en-us/library/19z1t1wy.aspx

	# optimizations
	cxx_omit_frame_pointer = /Oy
	cxx_disable_optimizations = /Od
	cxx_full_optimizations = /Ox
	cxx_size_optimizations = /O1
	cxx_speed_optimizations = /O2

	# code generation
	cxx_exceptions = /EHsc
	# TODO not sure about this one
	cxx_no_exceptions = /EHsc-
	cxx_seh_exceptions = /EHa
	cxx_whole_program_optimizations = /GL
	cxx_rtti = /GR
	cxx_no_rtti = /GR-
	cxx_clr = /clr
	cxx_clr_pure = /clr:pure
	cxx_clr_safe = /clr:safe
	cxx_multithread_compilation = /MP
	cxx_mimimal_rebuild = /Gm
	cxx_no_mimimal_rebuild = /Gm-
	cxx_floatpoint_fast = /fp:fast
	cxx_floatpoint_strict = /fp:strict
	cxx_cdecl = /Gd
	cxx_fastcall = /Gr
	cxx_stdcall = /Gz
	cxx_vectorcall = /Gv
	cxx_avx = /arch:AVX
	cxx_avx2 = /arch:AVX2
	cxx_sse = /arch:SSE
	cxx_sse2 = /arch:SSE2
	cxx_sse3 = /arch:SSE2
	cxx_ssse3 = /arch:SSE2
	cxx_sse4.1 = /arch:SSE2

	# language
	cxx_symbols = /Z7
	cxx_omit_default_lib = /Zl
	cxx_11 =
	cxx_14 =

	# linking
	cxx_runtime_static_debug = /MTd
	cxx_runtime_dynamic_debug = /MDd
	cxx_runtime_static_release = /MT
	cxx_runtime_dynamic_release = /MD

	# miscellaneous
	cxx_fatal_warnings = /WX
	cxx_extra_warnings = /W4
	cxx_no_warnings = /W0

	# linker flags
	ld_no_incremental_link = /INCREMENTAL:NO
	ld_no_manifest = /MANIFEST:NO
	ld_ignore_default_libs = /NODEFAULTLIB
	ld_symbols = /DEBUG
	ld_shared_lib = /DLL

	# transformers
	defines =
	includedirs =
	disable_warnings =
	libdirs =
	libs =
	ignore_default_libs =
	transformer defines: /D${param}
	transformer includedirs: /I${rel_path}${param}
	transformer disable_warnings: /wd${param}
	transformer libdirs: /LIBPATH:${rel_path}${param}
	transformer libs: ${param}.lib
	transformer ignore_default_libs: /NODEFAULTLIB:${param}

	# main flags
	cxxflags = $cxx_exceptions
	ldflags =
	libflags =
	filter variation:debug
		cxxflags += $cxx_disable_optimizations $cxx_symbols
		ldflags += $ld_symbols
	filter variation:release
		cxxflags += $cxx_speed_optimizations

filter toolset:clang
	# clang suport
	cc = clang
	cxx = clang++

filter toolset:gcc
	# gcc support
	cc = gcc
	cxx = g++

filter toolset: r"gcc|clang"
	rule cc
		command = $cc -c $in -o $out -MMD $cxxflags $defines $includedirs
		description = cc $in
		depfile = $out.d
		deps = gcc
		expand = true

	rule cxx
		command = $cxx -o $out -MMD $cxxflags $defines $includedirs -c $in
		description = cxx $in
		depfile = $out.d
		deps = gcc
		expand = true

	rule lib
		command = ar rcs $out $in
		description = ar $in

	rule link
		command = $cxx $ldflags $frameworks $libdirs $in -o $out $libs
		description = link $out

	rule link_so
		command = $cxx -shared -fPIC $ldflags $frameworks $libdirs -o $out $in $libs
		description = cxx $in

	# extensions transformers and auto
	filter system: r"^(?i)(?!windows).*$"
		auto r"^(?i).*\.o$": cxx r"^(?i).*\.(cpp|cxx|cc|c\+\+)$"
		auto r"^(?i).*\.o$": cc r"^(?i).*\.c$"
		auto r"^(.*\/)?[^.\/]+$": link r"^(?i).*\.o$"
			# on Darwin systems we do a trick with dynamic libs
			# we ask loader to look for .so files next to executable
			# so executables can be loaded from any cwd
			# it's similar to how it works on Windows by default
			filter system: Darwin
				ldflags += -rpath @executable_path
		auto r"^(?i).*\.so$": link_so r"^(?i).*\.o$"
			filter system: Darwin
				ldflags += -install_name @rpath/$targets_explicit_name_0
		auto r"^(?i).*\.a$": lib r"^(?i).*\.(o|a)$"
		transformer application: ${param}
		transformer objects: ${param}.o
		transformer library: ${path}lib${file}.a
		transformer shared_library: ${path}lib${file}.so
	filter system: r"^(?i)windows$"
		auto r"^(?i).*\.o$": cxx r"^(?i).*\.(cpp|cxx|cc|c\+\+)$"
		auto r"^(?i).*\.o$": cc r"^(?i).*\.c$"
		auto r"^(?i).*\.exe$": link r"^(?i).*\.o$"
		auto r"^(?i).*\.dll$": link_so r"^(?i).*\.o$"
		auto r"^(?i).*\.a$": lib r"^(?i).*\.(o|a)$"
		transformer application: ${param}.exe
		transformer objects: ${param}.o
		transformer library: ${path}lib${file}.a
		transformer shared_library: ${path}lib${file}.dll

	# Clang flags
	# more info here http://clang.llvm.org/docs/CommandGuide/clang.html
	# TODO:

	# optimizations
	cxx_omit_frame_pointer = -fomit-frame-pointer
	cxx_disable_optimizations = -O0
	cxx_full_optimizations = -O3
	cxx_size_optimizations = -Os
	cxx_speed_optimizations = -Ofast

	# code generation
	cxx_exceptions = -fexceptions
	cxx_no_exceptions = -fno-exceptions
	cxx_whole_program_optimizations = -O4
	cxx_rtti = -frtti
	cxx_no_rtti = -fno-rtti
	cxx_floatpoint_fast = -funsafe-math-optimizations
	cxx_floatpoint_strict = -ffloat-store
	cxx_avx = -mavx
	cxx_avx2 = -mavx2
	cxx_sse = -msse
	cxx_sse2 = -msse2
	cxx_sse3 = -msse3
	cxx_ssse3 = -mssse3
	cxx_sse4.1 = -msse4.1

	# language
	cxx_symbols = -g
	cxx_11 = -std=c++11
	cxx_14 = -std=c++14

	# miscellaneous
	cxx_fatal_warnings = -Werror
	cxx_extra_warnings = -Wall -Wextra
	cxx_no_warnings = -w

	# linker flags
	ld_ignore_default_libs = -nodefaultlibs

	# transformers
	defines =
	includedirs =
	libdirs =
	libs =
	frameworks =
	transformer defines: -D${param}
	transformer includedirs: -I${rel_path}${param}
	transformer libdirs: -L${rel_path}${param}
	transformer libs: -l${param}
	filter system: Darwin
		transformer frameworks: -framework ${param}
	filter system: r"^(?i)(?!darwin).*$"
		# don't enable this with gcc/clang on non Darwins
		transformer frameworks:

	# main flags
	cxxflags =
	filter system: r"^(?i)(?!windows).*$"
		# don't enable this with gcc/clang on Windows
		# TODO: We shouldn't have it enabled for every object file.
		# But we need it to build object files of the shared libraries.
		cxxflags = -fPIC
	ldflags =
	filter variation:debug
		cxxflags += $cxx_symbols
		ldflags += $cxx_symbols
"""

# main app -----------------------------------------------------------

def main(*argv, **kwargs):
	# find out if user wants help about flags or something and slice all arguments after help
	arg_help = [sys.argv.index(v) for v in ["-h", "--help"] if v in sys.argv]
	arg_help = sys.argv[min(arg_help) + 1:] if arg_help else None
	if arg_help:
		lines = fox_core.split("\n")
		for arg in arg_help:
			# find stuff
			results = [index for index in range(0, len(lines)) if arg in lines[index]]
			# look behind/ahead
			results = [set([item for item in range(index - 1, index + 2) if item >= 0 and item < len(lines)]) for index in results]
			# merge context groups
			# so if we have [(0,1,2), (1,2,3)] we will have [(0,1,2,3)]
			merged_results = []
			while results:
				head = results[0]
				tail = results[1:]
				last_len = -1
				while len(head) > last_len:
					last_len = len(head)
					new_tail = []
					for rest in tail:
						if head.intersection(rest):
							head |= rest
						else:
							new_tail.append(rest)
					tail = new_tail
				merged_results.append(head)
				results = tail
			results = merged_results
			# merge strings
			results = "\n...\n".join(["\n".join([lines[item] for item in sorted(group)]) for group in results])
			# print results
			if results:
				print("results for %s:" % arg)
				print("...")
				print(results)
				print("...")
			else:
				print("no results for %s" % arg)
		exit(0)

	# parse arguments normally
	title = "buildfox ninja generator %s" % VERSION
	argsparser = argparse.ArgumentParser(description = title, add_help = False)
	argsparser.add_argument("-i", "--in", help = "input file", default = "build.fox")
	argsparser.add_argument("-o", "--out", help = "output file", default = "build.ninja")
	argsparser.add_argument("-w", "--workdir", help = "working directory")
	argsparser.add_argument("variables", metavar = "name=value", type = str, nargs = "*", help = "variables with values to setup", default = [])
	#argsparser.add_argument("-v", "--verbose", action = "store_true", help = "verbose output") # TODO
	argsparser.add_argument("--ide", help = "generate ide solution (vs, vs2012, vs2013, vs2015, xcode, make, qtcreator, cmake)", default = None, dest = "ide")
	argsparser.add_argument("--ide-prj", help = "ide project prefix", default = "build")
	argsparser.add_argument("--ide-env", help = "run provided command to set required environment before calling ninja from the ide, " +
		"use set NAME=VALUE form if you need to modify environment so it will work with all IDE's", default = None)
	argsparser.add_argument("--no-core", action = "store_false",
		help = "disable parsing fox core definitions", default = True, dest = "core")
	argsparser.add_argument("--no-env", action = "store_false",
		help = "disable environment discovery", default = True, dest = "env")
	argsparser.add_argument("-n", "--ninja-ide-gen", action = "store_true",
		help = "enables ninja ide generator mode (equal to --no-core --no-env)", default = False, dest = "ninja_ide_gen")
	argsparser.add_argument("--selftest", action = "store_true",
		help = "run self test", default = False, dest = "selftest")
	argsparser.add_argument("-v", "--ver", "--version", action = "version", version = title)
	argsparser.add_argument("-h", "--help", metavar = "REQUEST", type = str, nargs = "*",
		default = argparse.SUPPRESS, help = "look for request or show this help message and exit")
	args = vars(argsparser.parse_args())
	if "help" in args:
		argsparser.print_help()
		exit(0)

	if args.get("ninja_ide_gen"):
		args["core"] = False
		args["env"] = False
		args["in"] = "build.ninja" if args.get("in") == "build.fox" else args.get("in")
		args["out"] = ""

	if args.get("workdir"):
		os.chdir(args.get("workdir"))

	engine = Engine()

	if args.get("env"):
		env = discover()
		for name in sorted(env.keys()):
			engine.on_assign((name, env.get(name), "="))

	for var in args.get("variables"):
		parts = var.split("=")
		if len(parts) == 2:
			name, value = parts[0], parts[1]
			engine.on_assign((name, value, "="))
		else:
			raise SyntaxError("unknown argument '%s'. you should use name=value syntax to setup a variable" % var)

	if args.get("core"):
		engine.load_core(fox_core)

	if args.get("selftest"):
		fox_filename, ninja_filename, app_filename = selftest_setup()
		engine.load(fox_filename)
		engine.save(ninja_filename)
		result = not subprocess.call(["ninja", "-f", ninja_filename])
		if result:
			result = not subprocess.call(["./" + app_filename])
		if result:
			print("Selftest - ok")
			selftest_wipe()
		else:
			print("Selftest - failed")
			sys.exit(1)
	else:
		engine.load(args.get("in"))
		if len(args.get("out")):
			engine.save(args.get("out"))

		ide = args.get("ide")

		if ide in ["vs", "vs2012", "vs2013", "vs2015"]:
			if ide == "vs":
				ide = "vs" + engine.variables.get("toolset_msc_ver", "")
			gen_vs(
				engine.context.all_files,
				cxx_defines(engine.variables.get("defines", "")),
				cxx_includedirs(engine.variables.get("includedirs", "")),
				args.get("ide_prj"),
				ide,
				args.get("ide_env"))
		elif ide in ["xcode"]:
			gen_xcode(
				engine.context.all_files,
				cxx_includedirs(engine.variables.get("includedirs", "")),
				args.get("ide_prj"),
				args.get("in"),
				args.get("ide_env"),
				args.get("ninja_ide_gen"))
		elif ide in ["make"]:
			gen_make(
				args.get("in"),
				args.get("ide_env"),
				args.get("ninja_ide_gen"))
		elif ide in ["qtcreator"]:
			gen_qtcreator(
				engine.context.all_files,
				cxx_defines(engine.variables.get("defines", "")),
				cxx_includedirs(engine.variables.get("includedirs", "")),
				args.get("ide_prj"),
				args.get("in"),
				args.get("ide_env"),
				args.get("ninja_ide_gen"))
		elif ide in ["cmake"]:
			gen_cmake(
				engine.context.all_files,
				cxx_includedirs(engine.variables.get("includedirs", "")),
				args.get("ide_prj"),
				args.get("in"),
				args.get("ide_env"))
		elif ide is not None:
			raise ValueError("unknown ide '%s', available ide's : vs, vs2012, vs2013, vs2015, xcode, make, qtcreator, cmake" % ide)

if __name__ == "__main__":
	#import cProfile, pstats, io
	#pr = cProfile.Profile()
	#pr.enable()
	main()
	#pr.disable()
	#s = io.StringIO()
	#sortby = "cumulative"
	#ps = pstats.Stats(pr, stream = s).sort_stats(sortby)
	#ps.print_stats()
	#print(s.getvalue())
