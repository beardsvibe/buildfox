# Mask IR proposal (WIP)

## Philosophy

There are "build systems", and they build dependency trees between sources and targets,
[some of them](https://martine.github.io/ninja/) are doing it really good.
There are also "project generators", they make decisions how and what to build,
they usually provide abstractions for packages, toolsets, etc.

Mask aims to be intermediate media between.

## Format

Mask IR format is designed to be a source for project or make file generation,
it's more or less mimic ninja format, but adds information required for sensible
project generation.

Some ninja features were removed from grammar
* default
* depfile/deps/msvc_deps_prefix **TODO do we want to remove it or not ?**
* pools/console
* builddir
* ninja_required_version
* include, subninja (last replaced with import)

And some features were added :
* packages - project context information, so we can generate sensible project trees for IDE's
* import - same as subninja
* auto - magic rule

	# your usual ninja format
	cflags = -Wall
	ldflags = -Wall

	rule cc
		command = gcc $cflags -c $in -o $out 
	rule ld
		command = gcc $ldflags -o $out $in

	build foo.o: cc foo.c
	build foo: ld foo.o
		lflags = # you can shadow commands like this

Next line will create project in IDE and add target('s) dependency tree to that project
* Mask runtime will traverse through dependency tree and look for start nodes (usually source files)
and this source files will end-up in project tree if their format is applicable
* Mask also will try to find most common configurations for toolset
and use this configuration as "project default" for tree-based project file formats like MSVS or XCode

	package test: foo

If you want to specify build variations you can do it like this : **TODO fix this shit**

	build foo_debug: phony ...
	build foo_release: phony ...
	package test: foo_debug foo_release
		variations = debug release 
		debug = foo_debug # TODO
		release = foo_release # TODO

In some cases you don't want to write rules with details about toolset (or it's just not applicable),
in this case we will help you with our toolset utility - magic "auto" rule.

	build foo.o: auto foo.cpp

Auto rule analyse input, output, toolset options, some variables, etc, and generate command line for you.
This rule follow same namescope rules as everything else (you can shadow variables, etc), so you can read or shadow this variables.
Some variables that auto rule use : **TODO**
* auto_toolset - msvc, gcc, clang, etc
* auto_variation - debug or release
* auto_cflags
* auto_cppflags
* auto_ldflags

**TODO** Some ideas : maybe we can incorporate filters from premake somehow to simplify configuration setting per target variation ?
