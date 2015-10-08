#!/usr/bin/env python

# BuildFox ninja generator

import os
import re
import copy
import argparse

from lib_engine import Engine
from lib_environment import discover

# core definitions -----------------------------------------------------------

fox_core = r"""
# buildfox core configuration

# buildfox relies on scoped rules and they were added in ninja v1.6
ninja_required_version = 1.6

filter toolset:msvc
	# msvc support
	cxx = cl
	lib = lib

	rule cxx
		command = $cxx $cxxflags $defines $includedirs $disable_warnings /nologo /showIncludes -c $in /Fo$out
		description = cxx $in
		deps = msvc
		expand = true

	rule link
		command = $cxx /nologo @$out.rsp /link $ldflags $libdirs $ignore_default_libs /out:$out
		description = link $out
		rspfile = $out.rsp
		rspfile_content = $in

	rule link_dll
		command = $cxx /nologo @$out.rsp /link /DLL $ldflags $libdirs $ignore_default_libs /out:$out
		description = link $out
		rspfile = $out.rsp
		rspfile_content = $in

	rule lib
		command = $lib $libflags @$out.rsp /nologo -OUT:$out
		description = lib $out
		rspfile = $out.rsp
		rspfile_content = $in

	auto r"(?i).*\.obj": cxx r"(?i).*\.(cpp|cxx|cc|c\+\+|c)$"
	auto r"(?i).*\.exe": link r"(?i).*\.(obj|lib)$"
	auto r"(?i).*\.dll": link_dll r"(?i).*\.(obj|lib)$"
	auto r"(?i).*\.lib": lib r"(?i).*\.(obj|lib)$"

	# extensions transformers
	transformer app: ${param}.exe
	transformer obj: ${param}.obj
	transformer lib: ${param}.lib
	transformer shlib: ${param}.dll
	transformer shlib_dependency: ${param}.lib

	# MSVC flags
	# more info here https://msdn.microsoft.com/en-us/library/19z1t1wy.aspx

	# optimizations
	cxx_omit_frame_pointer = /Oy
	cxx_disable_optimizations = /Od
	cxx_full_optimizations = /Ox
	cxx_size_optimizations = /O1
	cxx_speed_optimizations = /O2

	# code generation
	cxx_exceptions = /EHsc
	cxx_no_exceptions = /EHsc- # TODO not sure about this one
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

	# language
	cxx_symbols = /Z7
	cxx_omit_default_lib = /Zl

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
	ignore_default_libs =
	transformer defines: /D${param}
	transformer includedirs: /I${param}
	transformer disable_warnings: /wd${param}
	transformer libdirs: /LIBPATH:${param}
	transformer ignore_default_libs: /NODEFAULTLIB:${param}

	# main flags
	cxxflags =
	ldflags =
	libflags =
	filter variation:debug
		cxxflags = $cxx_disable_optimizations $cxx_symbols
		ldflags = $ld_symbols
	filter variation:release
		cxxflags = $cxx_speed_optimizations
		ldflags =

filter toolset:clang
	# clang suport
	cc = clang
	cxx = clang++

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
		expand = true

	rule link
		command = $cxx $ldflags $libdirs $in -o $out $libs
		description = link $out

	rule link_so
		command = $cxx -shared -fPIC $ldflags $libdirs -o $out $in $libs
		description = cxx $in
		expand = true

	auto r"(?i).*\.o": cxx r"(?i).*\.(cpp|cxx|cc|c\+\+)$"
	auto r"(?i).*\.o": cc r"(?i).*\.(c)$"
	auto r"^(.*\/)?[^.\/]+$": link r"(?i).*\.(o|a|so)$"
	auto r"(?i).*\.so": link_so r"(?i).*\.(o|so)$"
	auto r"(?i).*\.a": lib r"(?i).*\.(o|a)$"

	# extensions transformers
	transformer app: ${param}
	transformer obj: ${param}.o
	transformer lib: lib${param}.a
	transformer shlib: lib${param}.so
	transformer shlib_dependency: lib${param}.so

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
	cxx_avx = -mavx
	cxx_avx2 = -mavx2
	cxx_sse = -msse
	cxx_sse2 = -msse2

	# miscellaneous
	cxx_fatal_warnings = -Werror
	cxx_extra_warnings = -Wall -Wextra
	cxx_no_warnings = -w

	# transformers
	defines =
	includedirs =
	libdirs =
	libs =
	transformer defines: -D${param}
	transformer includedirs: -I${param}
	transformer libdirs: -L${param}
	transformer libs: -l${param}

	# main flags
	# TODO: We shouldn't have it enabled for every object file.
	# But we need it to build object files of the shared libraries.
	cxxflags = -fPIC
	ldflags = 
	filter variation:debug
		cxxflags += -g
		ldflags += -g
"""

# main app -----------------------------------------------------------

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
