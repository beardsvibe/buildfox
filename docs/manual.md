# BuildFox

**WIP document**

**TODO revisit this**

BuildFox is a minimalistic generator for [ninja build system](http://martine.github.io/ninja/). It's designed to take leverage on simplicity and straightforwardness of ninja. BuildFox tries its best to provide as simple as possible yet powerful and usable manifest format to explore how simple and beautiful build systems can be.

### Introduction

**TODO revisit this**

There are many build systems with declarative style manifests (for example cmake, premake, tundra, gradle, gyp, etc). In declarative type you tell build system what inputs are, what configuration is, and what kind of outputs you want to achieve, that's it. And then build system tries to figure out how to actually achieve this. Figuring out step is often called decision making step or configuration step. Next step is execution step - actual building by running compiler executables. Execution step is often delegated to simpler tools like make, nmake, jom, ninja, etc, though some systems like msbuild, tundra do build software on their own.

By providing declarative layer on top of execution step, build systems create a lot of overhead by doing many things implicitly. Because of this now build system developer need to assume what scenarios of build system user are. And build system needs to provide abstractions flexible enough to support all possible variations of uses cases.

In the end build system developers end up with [turing complete](https://en.wikipedia.org/wiki/Turing_completeness) declarative language (for example : [make](http://okmij.org/ftp/Computation/#Makefile-functional)), and build system users are learning how to use this language to solve their problems. How complicated this could be you ask ? Last time we checked (late 2015) [gradle](https://github.com/gradle/gradle) code base contained more then 4500 source files ...

BuildFox is different because of it's imperative manifest language - instead of saying to it what you want to achieve, you are saying how to actually achieve it. Build system helps you by providing premade definitions for common use cases, but in the end you are free to do whatever you want.

BuildFox is also designed to be very fast, it should take more then a second to translate a manifest to ninja build file.

### Using BuildFox

*Currently BuildFox is targeting C/C++ language support on all popular platforms, so following examples will be about those languages.*

Before we start with the manifest, let's explore how do we actually build a C/C++ executable from source code.

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
	build obj(*): auto *.cpp
	
	# linking executable
	build app(helloworld): auto obj(*)

First line is compiling object files from .cpp files, and second line is linking final application from object files. ```obj(*)``` is equal to ```*.obj``` on Windows and ```*.o``` on others machines. ```app(helloworld)``` is equal to ```helloworld.exe``` on Windows and ```helloworld``` on others machines. ```auto``` is a name of a rule which will build our output files (object or application) from inputs files (cpp or object) by calling required compiler executables.

What if we want to compile static library for target "lib" and dynamic library for target "sharedlib" ? Then we use filters :

	# building objects
	build obj(*): auto *.cpp

	filter target: lib
		# linking mylib.lib/.a
		build lib(mylib): auto obj(*)

	filter target: sharedlib
		# compiling mylib.dll/.so and .lib
		build shlib(mylib) | lib(mylib): auto obj(*)

To now to set target variable you just call ```buildfox target=sharedlib```.

**TODO**

### Writing your own BuildFox files

**TODO**

### BuildFox file reference

#### Print

For debug or other purposes you can use print operator.

	# comment
	foo = hello
	bar = bar
	
	# variables can be substituted as $name or ${name}
	print $foo ${bar} !


#### Variables

For variables we support set operator, add and remove operators.

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

**TODO**
