# GNU make

GNU make reference is too huge to grasp, so we will go with quick reference for now.

### Grammar

More info [here](https://www.gnu.org/software/make/manual/html_node/Quick-Reference.html)

	# comment

	output: inputs
		command_line # optional
		next_command # optional

	define variable
	define variable =
	define variable :=
	define variable ::=
	define variable +=
	define variable ?=
	endef

	undefine variable

	ifdef variable
	ifndef variable
	ifeq (a,b)
	ifeq "a" "b"
	ifeq 'a' 'b'
	ifneq (a,b)
	ifneq "a" "b"
	ifneq 'a' 'b'
	else
	endif

	include file
	-include file
	sinclude file

	override variable-assignment

	export

	export variable
	export variable-assignment
	unexport variable

	private variable-assignment

	vpath pattern path
	vpath pattern
	vpath

	# more functions, see reference
