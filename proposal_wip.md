# Mask IR proposal (WIP)

## Philosophy

There are "build systems", and they build dependency trees between sources and targets,
[some of them](https://martine.github.io/ninja/) are doing it really good.
There are also "project generators", they make decisions how and what to build,
they usually provide abstractions for packages, toolsets, etc.

Mask aims to be intermediate media between. Similar to ninja, all possible decisions should be made up front by mask generator. 

## Format

Mask IR format is super set of ninja format with additional information required for sensible project generation.

Some ninja features were removed from grammar :

* default
* builddir
* ninja\_required\_version
* include, subninja (replaced with import)
* depfile/deps/msvc\_deps\_prefix **TODO do we want to remove it or not ?**
* pools/console **TODO do we want to remove it or not ?**

And some features were added :

* packages - project context information, so we can generate sensible project trees for IDE's
* variation - variation in package
* import - same as subninja
* raw - pass raw data to result project file

Code looks like this :

	# your usual ninja format
	cflags = -Wall
	ldflags = -Wall

	rule cc
		command = gcc $cflags -c $in -o $out 
	rule ld
		command = gcc $ldflags -o $out $in

	build foo.o: cc foo.c
	build foo: ld foo.o
		lflags = some flags # you can shadow commands like this

Next line will create project in IDE and add target('s) dependency tree to that project.

* Mask runtime will traverse through dependency tree and look for start nodes (usually source files)
and this source files will end-up in project tree if their format is applicable
* Mask also will try to find most common configurations for toolset
and use this configuration as "project default" for tree-based project file formats like MSVS or XCode

** TODO can we simplify it more ? **
So in result code looks like this :

	variation foo_debug: debug targets
		name = "debug"
	variation foo_release: release targets
	package test: foo_debug foo_release

We realise that in some cases there is need to pass custom data to result file, so it's possible like this :

	raw "I will end up as is in output project file"
	# note you will need to specify additional information (through variables)
	# for some generators like msvc, xcode, etc

### Toolset database

To generate mask IR you need extensive knowledge about your toolsets. You can implement this on your own, or you can use provided json configurations.

For example msvc.json :

	{
		"commands":
		{
			"c->obj": "cl $cflags -c $in $out"
			"cpp->obj": "cl $cflags -c $in $out"
			"obj->exe": "cl $lflags /link -o $out $in"
			...
		},
		"flags":
		{
			"cflags":
			{
				"debug": "..."
				"fast": "..."
				"size": "..."
				...
			},
			"lflags":
			{
				...
			}
		},
		"ext_object": ".obj"
		"ext_lib_static": ".lib"
		"ext_lib_dynamic": ".dll"
		...
	}

### Fox Mask

Fox Mask is a mask technology demonstrator, aka minimalistic build system which takes benefits of mask IR.

Language is a super set of mask IR, with some additions :

* auto rule, it will try to guess how to build your target from provided inputs
* scope filters similar to premake5

So example will be :

	# fox mask will scan toolsets definition to understand semantic of inputs and targets
	# this semantic will be used to actual command line generation
	# plus it will be used for correct naming on different platforms
	# if we compile this example on windows/msvc we will get somelib.lib
	# and fox mask will take care to change extension in appropriate entries in dependency graph
	build somelib.a: auto code.cpp

	# filter command accept list of strings
	# each string is pair "key:expr", expr is just value, or values with logic operands "or" and "not"
	# and value could be just string, or wildcard string or regex (regex is surrounded by forward slashes)
	# so simple example is :
	filter "toolset:msvc"
		cflags = "..."

	# in contrast with other commands, variables in filter will actually influence parent namescope directly
	# note, variable setup is still done from top to bottom
	# so if you want to change your compiler flags, please set filters before rules and build commands

	# if you want to compile to conditions
	filter "toolset:msvc" "machine:x64"
		cflags = "..."

	# or more complicated one
	# so this will only set on msvc 12 with targets x86 or x64
	filter "toolset:msvc" "machine:x86 or x64" "msvc_version:/.*12.*$/"
		cflags = "..."

	# to simplify variations setup we just filter our flags
	# fox mask will come with many filters predefined, for example this two will be predefined
	filter "variation:debug"
		auto_cflags = "debug"
	filter "variation:release"
		auto_cflags = "speed"

	build main.obj: auto main.cpp
	build main.exe: auto main.obj
	build other.exe: auto other.cpp

	# package setup is same with mask
	variation main_debug: main.exe
		name = "debug"
	variation main_release: main.exe
		name = "release"
	package main: main_debug main_release
