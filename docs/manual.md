# BuildFox

BuildFox is a minimalistic generator for [ninja build system](http://martine.github.io/ninja/). It's designed to take leverage on simplicity and straightforwardness of ninja. BuildFox tries its best to provide as simple as possible yet powerful and usable manifest format to explore how simple and beautiful build systems can be.

## Introduction

There are many build systems with declarative style manifests (for example cmake, premake, tundra, gradle, gyp, etc). In declarative type you tell build system what inputs are, what configuration is, and what kind of outputs you want to achieve, that's it. And then build system tries to figure out how to actually achieve this. Figuring out step is often called decision making step or configuration step. Next step is execution step - actual building by running compiler executables. Execution step is often delegated to simpler tools like make, nmake, jom, ninja, etc, though some systems like msbuild, tundra do build software on their own.

By providing declarative layer on top of execution step, build systems create a lot of overhead by doing many things implicitly. Because of this now build system developer need to assume what scenarios of build system user are. And build system needs to provide abstractions flexible enough to support all possible variations of uses scenarios.

In the end build system developers end up with [turing complete](https://en.wikipedia.org/wiki/Turing_completeness) declarative language (for example : [make](http://okmij.org/ftp/Computation/#Makefile-functional)), and build system users are learning how to use this language to solve their problems. How complicated this could be you ask ? Last time we checked (late 2015) [gradle](https://github.com/gradle/gradle) code base contained more then 4500 source files ...

BuildFox is different because of it's imperative manifest language - instead of saying to it what you want to achieve, you are saying how to actually achieve it. Build system helps you by providing premade definitions for common use cases, but in the end you are free to do whatever you want.

BuildFox is also designed to be very fast, it shouldn't take more then a second to translate a manifest to ninja build file.

## Using BuildFox

*Currently BuildFox is targeting C/C++ language support on all popular platforms, so following examples will be about those languages.*

Before we start with the manifest, let's explore how do we actually build an executable from C/C++ source code.

For Windows it usually looks like this :

	foo.cpp ----> foo.obj --+
	                        |---> app.exe
	bar.cpp ----> bar.obj --+

For *nix-like it often looks like this :

	foo.cpp ----> foo.o --+
	                      |---> app
	bar.cpp ----> bar.o --+

Most common way to create executable from C/C++ is to compile each source code file (.cpp) into related object file (.obj or .o), and then link them into final executable. This approach is used because if you change one source code file then you only need to recompile one object file and all other object files can be reused into link step.

You may ask why we need build systems if compiling executables is so easy ? Indeed compiling executable from source code is very easy from command line. The only problem is that compiler arguments, libraries, etc may differ between different platforms. Plus also in some cases you want to build your program differently depending on external arguments - in some cases you may want static library (.lib or .a) and in other cases you may want dynamic library (.dll or .so).

So the simplest way to build a simple application with BuildFox is just this :

	# building objects
	build objects(*): auto *.cpp
	
	# linking executable
	build application(helloworld): auto objects(*)

First line is compiling object files from .cpp files, and second line is linking final application from object files. ```objects(*)``` is equal to ```*.obj``` on Windows and ```*.o``` on others machines. ```application(helloworld)``` is equal to ```helloworld.exe``` on Windows and ```helloworld``` on others machines. ```auto``` is a name of a rule which will build our output files (object or application) from inputs files (cpp or object) by calling required compiler executables.

**Please mind that this one is incorrect :**

	build *.obj: auto *.cpp # will fail on non Windows machines or non MSC compiler
	build helloworld.exe: auto *.obj

What if we want to compile static library for target "lib" and dynamic library for target "sharedlib" ? Then we use filters :

	# building objects
	build objects(*): auto *.cpp

	filter target: lib
		# linking mylib.lib/.a
		build library(mylib): auto objects(*)

	filter target: sharedlib
		# compiling mylib.dll/.so and .lib
		build shared_library(mylib) | library(mylib): auto objects(*)

Now to set target you just call ```buildfox target=sharedlib```.

## Writing your own BuildFox files

#### Fox core and environment discovery

BuildFox contains two main parts : execution engine and fox core definitions (this architecture is somewhat similar to MSBuild). So when you run your own fox files, engine do environment discovery and executes fox core before your fox file is executed. This is needed so BuildFox can provide language and compiler support, so you can write your own platform-independed fox files at ease.

#### Apps

Usually it's very simple to build console apps :

	build objects(*): auto *.cpp
	build application(test): auto objects(*)

If you want to put object files and final executable in other folder, just add it :

	out = build_${variation} # this will form build_debug or build_release
	
	build objects($out/*): auto *.cpp
	build application($out/test): auto objects($out/*)

In case if you need to specify some compiler flags or defines :

	out = build_${variation} # this will form build_debug or build_release
	cxxflags = $cxx_speed_optimizations
	defines = TEST_DEFINE
	includedirs = some_folder
	
	build objects($out/*): auto *.cpp
	build application($out/test): auto objects($out/*)

#### Static libs

To build static library we just change target name transform to lib.

	build objects(*): auto *.cpp
	build library(test): auto objects(*)

And then to use this library in application we add it to libs and use all libs as implicit dependency

	build objects(lib/*): auto lib/*.cpp
	build library(lib/test): auto objects(lib/*)
	
	build objects(*): auto *.cpp
	build application(test): auto objects(*) | library(lib/*)
		libs += test
		libdirs += lib

#### Shared libs

Compiling shared libs is almost the same as static lib, plus you need to add "library" as implicit target because in some cases linking shared library produces static library as well.

	build objects(lib/*): auto lib/*.cpp
	build shared_library(lib/test1) | library(lib/test1): auto objects(lib/*)
	
	build objects(*): auto *.cpp
	build application(app): auto objects(*) | shared_library(lib/*)
		libs += test1
		libdirs += lib

If you develop shared libraries for Windows then you also need to mark symbols for export with approach of your choice, one way could be to use [__declspec(dllexport)]( https://msdn.microsoft.com/en-us/library/a90k134d.aspx).

## BuildFox file reference

#### Comments

Comments can be only on empty lines.

	# comment
	a = 1

#### Print

For debug or other purposes you can use print operator.

	foo = hello
	bar = bar
	
	# variables can be substituted as $name or ${name}
	print $foo ${bar} !

#### Variables

For variables we support set, add and remove operators.

	var = foo
	print $var
	# prints "foo"
	
	var += bar
	print $var
	# prints "foo bar"
	
	var -= bar
	print $var
	# prints "foo"

Please not that in first case var stricly is equal ```foo```, but in second and last case we preserve whitespace so we add ``` bar``` and remove ``` bar```. So we can make as follows :

	var = foo
	print $var
	# prints "foo"
	
	var +=     bar
	print $var
	# prints "foo     bar"
	
	var -= bar
	print $var
	# prints "foo    "

Variable name also can contain values of other variables

	foo = bar
	${foo}_value = test
	
	# will print test
	print $bar_value

#### Transformer

In some cases we need to slightly transform values by appending or prepending something depending on environment. For example if we mean static library then it will be prepended with .lib on Windows and .a on Linux.

	transformer test: very ${param}
	test = doge wow
	
	# will print very doge very wow
	# transformer works by splitting input line by spaces
	# replacing items with template and joining them back with spaces
	# this one is useful for something like defines or lib variables
	# which need to prepend/append some extra strings to each item
	print $test
	
	transformer img: ${param}.png
	rule some_rule
	
	# also transformers are used to modify file names based on environment
	# note you can only use this form in path
	build img(name): some_rule some_files
	
	# and if you want to add prefix just use transformer like this :
	transformer img2: ${path}prefix_${file}.png
	build img2(somepath/somename): some_rule some_files
	
	# please note that you cannot use transformer inside a path
	build somepath/img2(somename): some_rule some_files # invalid

#### Build commands

To build target (outputs) from inputs we use build commands.

	rule example
		command = cp $in $out
	
	# will copy a.txt to b.txt
	build b.txt: example a.txt
	
	rule example2
		command = cat $in $out $somevar $somevar2
	somevar = 0
	
	# should print "e.txt f.txt a.txt b.txt 1 2"
	# in this case :
	# - a.txt and b.txt are explicit targets
	#   they will be passed to the rule in $out variable
	# - c.txt and d.txt are implicit targets
	#   they are not passed to the rule, but we know that command will generate them
	# - e.txt and f.txt are explicit inputs
	#   they will be passed to the rule in $in variable
	# - g.txt and h.txt are implicit inputs
	#   they are not passed to the rule
	#   but we know that targets should be build after this file are built
	#   and we also know that we should rebuild targets if implicit inputs change
	# - i.txt and j.txt are order only inputs
	#   they are not passed to the rule
	#   but we know that targets should be build after this file are built
	#   targets will not be rebuild if order only inputs change
	build a.txt b.txt | c.txt d.txt: example2 e.txt f.txt | g.txt h.txt || i.txt j.txt
		# you can shadow rule variables from build command
		somevar = 1
		somevar2 = 2

Every path in BuildFox can be one of three types : normal path, regex, wildcard.

	# normal path
	build test.obj: cxx test.cpp
	
	# regex path
	# in this case it works similar to how regex replace works
	# input files regex create capture groups 1 and 2
	# and output files regex just use them as \2 and \1
	build r"\2_\1.obj": cxx r"so(doge|wow)_(.*)\.cpp"
	
	# wildcard path
	# in this case wildcard transforms to regex internally
	# and each basic element converts to capture group
	build *.obj: cxx *.cpp
	
	# wildcard and regexes are interchangeable
	build r"obj_\2_\1.obj": cxx *_*.cpp
	
	# any file except for specified name
	build *.obj: cxx "!(name|another_name).cpp"
	
	# recursive glob
	build **/*.obj: cxx **/*.cxx
	
	# recursive glob with concatenation in output
	# so a/b/c.cxx will become a_b_c.obj
	build *.obj: cxx **/*.cxx
	
	# advanced recursive glob
	build **/**/*.obj: cxx **/test/**/*.cxx
	
	# recursive glob with folder filtering
	build **/*.obj: cxx "*!(folder|another_folder)/*.cxx"

#### Filters

Filter allow us to evaluate scope depending on variable state.

	a = 2
	
	# filter nested scope is only evaluated if a = 1 or a = 2
	filter a: 1
		b = 1
	filter a: 2
		b = 2
	
	# filters also can be nested
	filter a: 2
		filter b: 1
			c = 1
		filter b: 2
			c = 2
	
	# should print 2 2 2
	print $a $b $c
	
	# filter value also can be regex or wildcard
	test = foo
	filter test: r"foo|bar"
		result = $test
	filter test: ?oo
		result += works
	# should print foo works
	print $result
	
	# you can filter all other operations like build, rules, etc
	filter c: 2
		print filter on $c
	
	# you can also filter nested variables
	# but in this case filters will only work with global namescope
	a = 1
	b = 2
	rule test
		filter a: 1
			b = 2
			filter a: 2
				c = 3 # this one is fine
		d = 4
		filter d: 4 # this is incorrect, you can only filter based on global namescope
			e = 5

#### Rules

Rules define executable command, form arguments and process dependency information. BuildFox is using ninja rules more or less as is (except for expand), so for more details please refer to [ninja manual](http://martine.github.io/ninja/manual.html#ref_rule).

	# rule have just a name and set of nested variables
	rule test
		# values of this variables are not evaluated in BuildFox (except for expand)
		# instead they are evaluated by ninja on moment when rule in triggered
		# by build command
		
		# command is required variable
		command = some_app $in $out
		# optional description for build log
		description = building $out
	
	# in case of cpp related rules we have depfile and deps commands
	rule cxx
		command = gcc -o $out -MMD -c $in 
		# -MMD flag asks gcc to output implicit dependencies information like user includes
		# this line asks ninja to parse this information and add it to build graph
		deps = gcc
		
		# gcc provides dependency information through dependecy file (.d)
		# this line asks ninja to remove this file after the command is finished
		depfile = $out.d
	
	# for Windows we have commands to use response file
	rule lib
		command = lib @$out.rsp /nologo -OUT:$out
		# this will create response the file with rspfile_content before running a command
		# and ninja will remove the file after a command is finished
		rspfile = $out.rsp
		
		# this sets the content of a response file
		rspfile_content = $in $libs
	
	# expand tells BuildFox to expand the rule over sets of file
	# expand variable is captured by the BuildFox engine and not passed to ninja
	rule cxx
		command = ...
		expand = true
	
	build *.obj: cxx *.cpp
	# let's imagine that we have a.cpp, b.cpp and c.cpp
	# first BuildFox will do wildcard lookup and find all input files
	# and it will generated list of related output files
	#
	# so after this our command will look like this :
	# build a.obj b.obj c.obj: cxx a.cpp b.cpp c.cpp
	# this is not what we actually wanted, so we set expand = true
	# to tell BuildFox to create multiple build commands for this rule
	# so we will get :
	# build a.obj: cxx a.cpp
	# build b.obj: cxx b.cpp
	# build c.obj: cxx c.cpp

Also there is the phony rule that can be used to create alises.

	# later you can just run ninja docs and it will build the docs
	build docs: phony doc1.txt doc2.txt ...

#### Auto

To simplify writing build commands we have auto rule. It will compare inputs and outputs of build command with known rules and insert correct rule for a case.

	# just rules
	rule cxx
		command = ...
	rule link
		command = ...
	
	# auto have output and input masks which can be value, wildcard or regex
	# and it also says which rule to use for this masks
	auto *.obj: cxx *.cpp
	auto *.exe: link *.obj
	
	# so now instead of specifying a rule we can just write auto
	build *.obj: auto *.cpp
	build *.exe: auto *.obj

#### Default

By default ninja will start building all targets that are not appear as inputs to any other targets. Sometimes it's useful to build just some targets by default, and build others targets (like docs, etc) only when we explicitly ask them to be built.

	# we build some apps
	...
	build foo.exe: auto foo/*.obj
	build bar.exe: auto bar/*.obj
	
	# and we specify default
	# multiple defaults are also possible
	default foo.exe
	
	# now when we run ninja it will only build foo.exe
	# and too built bar.exe we need to run "ninja bar.exe"

#### Subfox and include

To import or include another fox file from ours we use subfox or import commands. The difference between them is that import is not changing your local scope, on other hand include just pastes other fox file into yours.

	# subfox will not change your local variables, and will not introduce new rules
	# useful for adding libraries or other projects into yours
	subfox other_file.fox
	
	# include will just put file content into yours
	# useful for adding rules, setting variables, etc
	include some_file.fox
	
	# and of couse you can use wildcards or regexes
	subfox *.fox
	
	# to be compatible with ninja BuildFox also allow to use subninja command, which equal to subfox
	subninja *.ninja

#### Pool

Pools allow you to restrict how many usages of a rule are executed in parallel. For more details please refer to [ninja manual](http://martine.github.io/ninja/manual.html#ref_pool)

	# only 2 or less rules can be runned in parallel
	pool heavy_job_pool
		depth = 2
	
	rule heavy
		command = ...
		pool = heavy_job_pool

## Fox core reference

Fox core configures rules, variables, transformers, auto rules, etc depending on environment discovery variables. This enables users to use same rules, variables, etc to target multiple toolsets.

#### Rules

All provided rules are available through auto rule.

Rule name        | Description
---------------- | --------------------------------------------
cxx              | compile cpp files to object files
cc               | compile c files to object files
link             | link object files into executable
link_so          | link object files into dynamic library
lib              | link object files into static library

You can override compiler executable from your fox file through ```cc```, ```cxx``` and ```lib``` variables.

#### Path transformers

You need to use different file extensions on different platforms, to support this fox core provides multiple useful path transformers.

Transformer name | Possible Values       | Description
---------------- | --------------------- | --------------------------------------------
application      | .exe or as is         | executable
objects          | .obj or .o            | object file
library          | .lib or .a            | static lib
shared_library   | .dll or .so           | shared lib

#### Compiler and linker configuration

To set compiler or linker flags you need to use configuration variables. This variables will be passed as-is to compiler or linker and we recommend using cxx_\* and ld_\* flags from flags table to set required arguments in cross platform fashion.

Variable                        | Description
------------------------------- | ----------------
cxxflags                        | compiler flags
ldflags                         | linker flags
libflags                        | static lib archiver flags

#### Compiler flags transformers

Some compiler flags are easier and better to specify as whitespace separated list, fox core provides set of transformers for this purpose. For example : ```defines = DEFINE1 DEFINE2```. Please note that this transformers are passed to compiler and linker directly without interaction with ```cxxflags``` or ```ldflags```.

Transformer name    | Possible Values       | Description
------------------- | --------------------- | --------------------------------------------
defines             | /D or -D              | sets defines
includedirs         | /I or -I              | sets includes directories
libdirs             | /LIBPATH or -L        | sets libs directories
libs                | .lib or -l            | sets system libs
frameworks          | none or -framework    | sets frameworks (OS X only)
disable_warnings    | /wd                   | disables warnings (msc only)
ignore_default_libs | /NODEFAULTLIB         | ignores default lib (msc only)

#### Compiler and linker flags

To be able to target multiple toolsets fox core provides a selection of compiler flags. You can use them like ```cxxflags = $cxx_someflag```.

More information about compiler flags is available on [msc page](https://msdn.microsoft.com/en-us/library/19z1t1wy.aspx) and [clang page](http://clang.llvm.org/docs/CommandGuide/clang.html).

Flag                            | Possible Values                         | Description
------------------------------- | --------------------------------------- | ----------------
cxx_omit_frame_pointer          | /Oy or -fomit-frame-pointer             |
cxx_disable_optimizations       | /Od or -O0                              |
cxx_full_optimizations          | /Ox or -O3                              |
cxx_size_optimizations          | /O1 or -Os                              |
cxx_speed_optimizations         | /O2 or -Ofast                           |
cxx_exceptions                  | /EHsc or -fexceptions                   |
cxx_no_exceptions               | /EHsc- or -fno-exceptions               |
cxx_seh_exceptions              | /EHa                                    | msc only
cxx_whole_program_optimizations | /GL or -O4                              |
cxx_rtti                        | /GR or -frtti                           |
cxx_no_rtti                     | /GR- or -fno-rtti                       |
cxx_clr                         | /clr                                    | msc only
cxx_clr_pure                    | /clr:pure                               | msc only
cxx_clr_safe                    | /clr:safe                               | msc only
cxx_multithread_compilation     | /MP                                     | msc only
cxx_mimimal_rebuild             | /Gm                                     | msc only
cxx_no_mimimal_rebuild          | /Gm-                                    | msc only
cxx_floatpoint_fast             | /fp:fast or -funsafe-math-optimizations |
cxx_floatpoint_strict           | /fp:strict or -ffloat-store             |
cxx_cdecl                       | /Gd                                     | msc only
cxx_fastcall                    | /Gr                                     | msc only
cxx_stdcall                     | /Gz                                     | msc only
cxx_vectorcall                  | /Gv                                     | msc only
cxx_avx                         | /arch:AVX or -mavx                      |
cxx_avx2                        | /arch:AVX2 or -mavx2                    |
cxx_sse                         | /arch:SSE or -msse                      |
cxx_sse2                        | /arch:SSE2 or -msse2                    |
cxx_sse3                        | /arch:SSE2 or -msse3                    |
cxx_ssse3                       | /arch:SSE2 or -mssse3                   |
cxx_sse4.1                      | /arch:SSE2 or -msse4.1                  |
cxx_symbols                     | /Z7 or -g                               |
cxx_omit_default_lib            | /Zl                                     | msc only
cxx_11                          | empty or -std=c++11                     |
cxx_14                          | empty or -std=c++14                     |
cxx_runtime_static_debug        | /MTd                                    | msc only
cxx_runtime_dynamic_debug       | /MDd                                    | msc only
cxx_runtime_static_release      | /MT                                     | msc only
cxx_runtime_dynamic_release     | /MD                                     | msc only
cxx_fatal_warnings              | /WX or -Werror                          |
cxx_extra_warnings              | /W4 or -Wall -Wextra                    |
cxx_no_warnings                 | /W0 or -w                               |
ld_no_incremental_link          | /INCREMENTAL:NO                         | msc only
ld_no_manifest                  | /MANIFEST:NO                            | msc only
ld_ignore_default_libs          | /NODEFAULTLIB or -nodefaultlibs         |
ld_symbols                      | /DEBUG                                  | msc only
ld_shared_lib                   | /DLL                                    | msc only

## Environment discovery reference

Environment discovery is responsible for figuring out which compiler to use, what current system is, etc. Environment discovery is executed before fox core and it only generates set of variables that are described in table below.

You can override this variables values by specifying them as BuildFox arguments.

Name            | Possible Values       | Description
--------------- | --------------------- | --------------------------------------------
variation       | debug                 | build variation, by default is always debug
toolset_msc     | true or not set       | true if msc toolset is available
toolset_msc_ver | 2012, 2013 or 2015    | version of msc toolset if it's available
toolset_clang   | true or not set       | true if clang toolset is available
toolset_gcc     | true or not set       | true if gcc toolset is available
toolset         | msc or clang or gcc   | preferred toolset to use, preferences : msc > clang > gcc
system          | [platform.system](https://docs.python.org/2/library/platform.html#platform.system) | current system os string
machine         | [platform.machine](https://docs.python.org/2/library/platform.html#platform.machine) | current machine arch name string
cwd             | path that ends with / | current working directory

## Special variables reference

BuildFox have some special variables that are processed differently from others.

Name                      | Possible Values       | Description
------------------------- | --------------------- | --------------------------------------------
buildfox_required_version | 0.1, etc              | sets required version of BuildFox from fox file
excluded_dirs             | .git .svn etc         | space separated list of ignored folders for recursive glob
rel_path                  | path that ends with / | relative path from cwd to location of current fox file, updated at runtime
