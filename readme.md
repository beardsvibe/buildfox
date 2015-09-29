# BuildFox

Minimalistic ninja generator

WIP

### Usage

Installation on windows :

	doskey buildfox=python %path_to_buildfox%\buildfox.py $*

Usage :

	buildfox
	ninja

Release build :

	buildfox -d variation release
	ninja

### Manifest

BuildFox manifest is a super set to ninja manifest.

Core features are :

- variable filtering
- regex/wildcard file names
- auto build rule

Example :

	# filtering	
	# value in filter could be wildcard or regex
	# TODO var-value-var-value separators
	filter var1:value_or_wildcard_or_regex var2:value_or_wildcard_or_regex
		var3 = value
		...
	
	# wildcard file names
	build *.exe: auto *.c
	
	# regex file names
	build r"\1\.exe": auto r"(.+)\.c"
	
	# configure auto build rule
	# all auto build commands with .obj targets and .cpp inputs will be converted to cxx
	auto *.obj: cxx *.cpp

### Generator

BuildFox is written in python and compatible with python 3.3+

App contains four main parts :

- Parser
- Engine
- Environment
- Fox Core - contains core definitions and toolset support
