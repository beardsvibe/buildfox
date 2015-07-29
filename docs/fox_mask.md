# Fox Mask

Fox Mask is a mask IR technology demonstrator, aka minimalistic build system which takes benefits of mask IR.

Language is a super set of ninja :

* auto rule, it will try to guess how to build your target from provided inputs
* scope filters similar to premake5

Example :

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

	# package setup is same with mask IR
	project main
		debug = main.exe
		release = ...
