# ninja build system format

### Grammar

	# this is ninja comment
	var_name = var_value

	ninja_required_version = 1.5 # if we use some cool features

	rule rule_name # spacing is two spaces
	  command = command_line_text $in some_other_text $out $var_name $in_newline # in in_newline inputs separated by newline
	  depfile = $out.d # for implicit dependencies in gcc/clang
	  deps = gcc # or msvc
	  description = tell me what is it in human text
	  msvc_deps_prefix = ... # only for non English msvs
	  generator = 1 # tell ninja that this reinvokes higher level build system
	  restat = 1 # ask ninja to check modification times of outputs, and if they are same outputs are threated as "not rebuilt"	
	  rspfile = $out.rsp # ninja creates this file with rspfile_content_content before calling command, and removes it afterwards, this is useful when command is longer then command line max limit
	  rspfile_content = $in  
	
	build target_file1 target_file2: rule_name input_file_1 input_file2
	build other_target: phony some_target
	build target: rule_name input | implicit_deps || order_only_deps # order only deps not cause target rebuild, but implicit deps do

	pool link_pool
	  depth = 4
	rule link
	  command = ...
	  pool = link_pool # execution of this rule will be limited to 4 concurrent jobs 

	rule advanced_stuff
	  command = ...
	  pool = console # predefined pool name with depth = 1, every job with this rule will get control over stdin, stdout and stderr

	default some_target some_other_target # if specified, we will only build specified targets if no other arguments given to ninja, useful for debug/release stuff
	subninja other_ninja_file.ninja # imports other file, other file gets private namescope which shadows current namescope
	include other_file.ninja # just includes other file as is

	build ... # not sure about this one 


### Escaping

TODO

### Interesting stuff

* Ninja is able to generate [llvm db](http://clang.llvm.org/docs/JSONCompilationDatabase.html)
* By default ninja will build all targets that no other targets are depends on (root's of the tree), but this could be changed with default keyword