# BuildFox deploy script
# compiles multiple files into one python script

import re
from pprint import pprint

re_lib_import = re.compile(r"^from (lib_\w+) import \w+((, \w+)+)?$", flags = re.MULTILINE)
re_import = re.compile(r"^import (\w+)$", flags = re.MULTILINE)

# return prepared text of BuildFox module
def file_text(name):
	with open(name, "r") as f:
		text = f.read()
		text = text.replace("#!/usr/bin/env python", "")
		text = text.replace("# BuildFox ninja generator", "")
		return text

# return license text
def license_text():
	text = open("../license", "r").readlines()
	text = ["# " + line if len(line) > 1 else "#\n" for line in text] # don't add space in empty lines
	text = "".join(text) + "\n"
	return text

# replace BuildFox imports
replaced = False
visited_files = set()
def replace_lib_import(matchobj):
	global replaced, visited_files
	name = matchobj.group(1)
	if name not in visited_files:
		visited_files.add(name)
		replaced = True
		return "%s" % file_text("../%s.py" % name)
	else:
		return ""

# put all BuildFox imports in one file
text = file_text("../buildfox.py")
replaced = True
while replaced:
	replaced = False
	text = re_lib_import.sub(replace_lib_import, text)

# place system imports on top
system_imports = set()
def replace_import(matchobj):
	global system_imports
	system_imports.add(matchobj.group(1))
	return ""
text = re_import.sub(replace_import, text)
system_imports = sorted(list(system_imports), key = lambda v: len(v))

# beautify whitespace
text = re.sub("\n\n+", "\n\n", text) # strip more then two new lines in a row
text = text.strip() # strip start and end whitespace
text += "\n" # ensure new line in the end

# figure out version
ver_major = re.search("^MAJOR = (\d+)$", text, flags = re.MULTILINE)
ver_minor = re.search("^MINOR = (\d+)$", text, flags = re.MULTILINE)

if ver_major and ver_minor:
	ver = "v%d.%d" % (int(ver_major.group(1)), int(ver_minor.group(1)))
else:
	ver = "version unknown"

print("BuildFox %s" % ver)

# write compiled version
with open("bf", "w") as f:
	f.write("#!/usr/bin/env python\n\n")
	f.write("# BuildFox ninja generator, %s\n\n" % ver)
	f.write(license_text())

	f.write("\n")
	for imp in system_imports:
		f.write("import %s\n" % imp)
	f.write("\n")

	f.write(text)
