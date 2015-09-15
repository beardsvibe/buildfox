
# tired of grako unable parse whitespace correctly
# lets see if it's easy to parse manifest by hand

import re
from pprint import pprint

re_newline_escaped = re.compile("\$+$")
re_comment = re.compile("(?<!\$)\#.*$") # looking for not escaped #
re_identifier = re.compile("[a-zA-Z0-9_.-]+")

with open("fox_parser_test2.ninja", "r") as f:
	lines = f.read().splitlines()
	i = 0
	while i < len(lines):
		line = ""

		# dealing with escaped newlines
		newline_escaped = True
		while newline_escaped and (i < len(lines)):
			line += lines[i]
			i += 1
			newline_escaped = re_newline_escaped.search(line)
			if newline_escaped:
				l, r = newline_escaped.span()
				# in some cases we can have $$, $$$$, etc in the end
				# which are escaped $ combinations, and they don't escape newline
				if (r - l) % 2:
					# in case if they do $, $$$, etc, we need to strip last one
					line = line[:-1]
				else:
					newline_escaped = None

		# line is ready for processing
		line_stripped = line.strip()

		# skip empty lines
		if not line_stripped:
			continue

		# strip comments
		if line_stripped[0] == "#":
			continue
		comment_eol = re_comment.search(line_stripped)
		if comment_eol:
			line_stripped = line_stripped[:comment_eol.span()[0]]
			line_stripped = line_stripped.strip()

		# find first identifier, next actions will be based on it
		identifier = re_identifier.search(line_stripped)
		if not identifier:
			print("Error, failed to parse '%s', cant find first identifier" % line)
		else:
			line_stripped = line_stripped[identifier.span()[1]:].strip()
			identifier = identifier.group(0)

		# key token identification
		if identifier == "rule":
			pass
		elif identifier == "build":
			pass
		elif identifier == "default":
			pass
		elif identifier == "pool":
			pass
		elif identifier == "include":
			pass
		elif identifier == "subninja":
			pass
		elif identifier == "filter":
			pass
		elif identifier == "auto":
			pass
		else:
			pass

		pprint(line)
			#pprint(line_stripped)
			#pprint(identifier)
