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

So in result code looks like this :

	variation foo_debug: debug targets
		name = "debug"
	variation foo_release: release targets
	package test: foo_debug foo_release

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
