# mask escaping functions
# "$\n" = "\n"
# "$ " = " "
# "$:" = ":"
# "$$" = "$"

# TODO escape for | ?

import re
def to_esc(str, escape_space = True):
	str = str.replace("$", "$$").replace(":", "$:").replace("\n", "$\n")
	
	if escape_space:
		str = str.replace(" ", "$ ")

	# TODO this is (facepalm) solution for variable escaping, fix it !
	def repl(matchobj):
		return "${" + matchobj.group(1) + "}"
	str = re.sub("\$\${([a-zA-Z0-9_.-]+)}", repl, str)
	return str

def from_esc(str):
	return str.replace("$\n", "").replace("$ ", " ").replace("$:", ":").replace("$$", "$")

def to_esc_iter(iter):
	return [to_esc(s) for s in iter]

def from_esc_iter(iter):
	return [from_esc(s) for s in iter]

def to_esc_shell(str):
	# TODO replace with shlex.quote on python 3.3+
	unsafe = ["\"", " "]
	if any(s in str for s in unsafe):
		return "\"" + str.replace(" ", "\\ ").replace("\"", "\\\"") + "\""
	else:
		return str
