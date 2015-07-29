# Compact IR format

### Intro

Some WIP stuff on better IR format

From [this](https://github.com/martine/ninja/blob/master/src/build_log_perftest.cc#L42-L61) we know :

	The average command length is 4.1 kB and there were 28674 commands in total,
	which makes for a total log size of ~120 MB (also counting output filenames).

Let's make some goals :

* (#1) Parsing and saving of compact IR file without need to reconstruct all data in memory in advance.
* (#2) Human readable format **???**
* (#3) Easily generated from existing build systems
* (#4) Parse raw 120 MB shell script into compact IR format in less then 1 second on modern machine with SSD.
* (#5) Translate this compacted IR file into raw 120 MB shell script in less then 1 second on modern machine with SSD.

### Gathering stuff

* Average command is long, but contains many common parts. In best case all arguments will be equal but filenames.
Many make-like build systems incorporate this as rules or macro.
* Programs can be divided into three types :
	* care about argument order
	* don't care about argument order
	* partially care about argument order
* We can't generally figure out if argument is filename or not (requires explicit knowledge about executed tool)

We can take split command line, take arguments, and find common sets. 
In some cases (mostly compilers\linkers) we can extract input and output filenames.

### Format structure

Format is subset of ninja manifest format with some limitations which make it possible to achieve (#1) (#2) (#3)

* strict order of declaration :
	* variable definitions first
	* rules second
	* build command third
* strict indentation rules : **??? could simplify parsing ???**
	* all lines, except for variables in rules, must contain no whitespace in the beginning
	* indent in rule and project variables is 2 spaces only
	* only one space is allowed between tokens
* no variable shadowing in build commands or rules, all variables are expanded immediately as they’re encountered, with no exceptions
* no includes or subninja, no variable scoping
* use implicit outputs instead of phony rules
* no default
* added project command

For example :

	# comment
	variable = ...

	rule rule_name
	  command = ...

	build target: rule_name input

	build target | target2: rule_name input | implicit_input || order_only_dep

	# specify project and variations
	project test
	  debug = target1 target2 ...
	  any_other_variation_name = ...