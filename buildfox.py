# BuildFox ninja generator
#
# The MIT License (MIT)
#
# Copyright (c) 2015 Dmytro Ivanov
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

import os
import re
import copy
import shutil
import argparse
import collections

# ----------------------------------------------------------- fox core definitions

fox_core = r"""
# buildfox core configuration

# buildfox relies on scoped rules and they were added in ninja v1.6
ninja_required_version = 1.6

filter toolset:msvc
	# msvc support
	rule cxx
		command = cl $cxxflags /nologo /showIncludes -c $in /Fo$out
		description = cxx $in
		deps = msvc
		expand = true

	rule link
		command = cl /nologo @$out.rsp /link $ldflags /out:$out
		description = link $out
		rspfile = $out.rsp
		rspfile_content = $in

	rule link_dll
		command = cl /nologo @$out.rsp /link /DLL $ldflags /out:$out
		description = link $out
		rspfile = $out.rsp
		rspfile_content = $in

	rule lib
		command = lib $libflags @$out.rsp /nologo -OUT:$out
		description = lib $out
		rspfile = $out.rsp
		rspfile_content = $in

	auto *.obj: cxx r".*\.(cpp|cxx|c)$"
	auto *.exe: link r".*\.(obj|lib)$"
	auto *.dll: link_dll r".*\.(obj|lib)$"
	auto *.lib: lib r".*\.(obj|lib)$"

	filter variation:debug
		cxxflags = /O1
		ldflags =
		libflags =

	filter variation:release
		cxxflags = /Ox
		ldflags =
		libflags =
"""

# ----------------------------------------------------------- constants

keywords = ["rule", "build", "default", "pool", "include", "subninja",
	"subfox", "filter", "auto", "print"]

# parser regexes
re_newline_escaped = re.compile("\$+$")
re_comment = re.compile("(?<!\$)\#(.*)$") # looking for not escaped #
re_identifier = re.compile("[a-zA-Z0-9\${}_.-]+")
re_path = re.compile(r"(r\"(?![*+?])(?:[^\r\n\[\"/\\]|\\.|\[(?:[^\r\n\]\\]|\\.)*\])+\")|((\$\||\$ |\$:|[^ :|\n])+)")

# engine regexes
re_var = re.compile("\${([a-zA-Z0-9_.-]+)}|\$([a-zA-Z0-9_-]+)")
re_folder_part = re.compile(r"(?:[^\r\n(\[\"\\]|\\.)+") # match folder part in filename regex
re_capture_group_ref = re.compile(r"(?<!\\)\\(\d)") # match regex capture group reference
re_variable = re.compile("\$\${([a-zA-Z0-9_.-]+)}|\$\$([a-zA-Z0-9_-]+)")
re_non_escaped_char = re.compile(r"(?<!\\)\\(.)") # looking for not escaped \ with char
re_alphanumeric = re.compile(r"\W+")

# ----------------------------------------------------------- args

argsparser = argparse.ArgumentParser(description = "buildfox ninja generator")
argsparser.add_argument("-i", "--in", help = "input file", default = "build.fox")
argsparser.add_argument("-o", "--out", help = "output file", default = "build.ninja")
argsparser.add_argument("-w", "--workdir", help = "working directory")
argsparser.add_argument("-d", "--define", nargs = 2, help = "define var value",
	default = [], action = "append")
#argsparser.add_argument("-v", "--verbose", action = "store_true", help = "verbose output") # TODO
argsparser.add_argument("--no-core", action = "store_false",
	help = "disable parsing fox core definitions", default = True, dest = "core")
argsparser.add_argument("--no-env", action = "store_false",
	help = "disable environment discovery", default = True, dest = "env")
args = vars(argsparser.parse_args())

# ----------------------------------------------------------- parser

class Parser:
	def __init__(self, engine, filename, text = None):
		self.engine = engine
		self.filename = filename
		self.whitespace_nested = None
		self.comments = []
		if text:
			self.lines = text.splitlines()
		else:
			with open(self.filename, "r") as f:
				self.lines = f.read().splitlines()

	# parse everything
	def parse(self):
		self.line_i = 0
		while self.next_line():
			# root objects must have zero whitespace offset
			if self.whitespace != 0:
				raise ValueError("unexpected indentation in '%s' (%s:%i)" % (
					self.line,
					self.filename,
					self.line_num
				))
			self.parse_line()

	def parse_line(self):
		self.command = self.read_identifier()

		self.engine.current_line = self.line
		self.engine.current_line_i = self.line_num

		if len(self.comments):
			for comment in self.comments:
				self.engine.comment(comment)
			self.comments = []

		if self.command == "rule":
			obj = self.read_rule()
			assigns = self.read_nested_assigns()
			self.engine.rule(obj, assigns)

		elif self.command == "build":
			obj = self.read_build()
			assigns = self.read_nested_assigns()
			self.engine.build(obj, assigns)

		elif self.command == "default":
			obj = self.read_default()
			assigns = self.read_nested_assigns()
			self.engine.default(obj, assigns)

		elif self.command == "pool":
			obj = self.read_pool()
			assigns = self.read_nested_assigns()
			self.engine.pool(obj, assigns)

		elif self.command == "include":
			obj = self.read_include()
			self.engine.include(obj)

		elif self.command == "subninja" or self.command == "subfox":
			obj = self.read_subninja()
			self.engine.subninja(obj)

		elif self.command == "filter":
			obj = self.read_filter()
			need_to_parse = self.engine.filter(obj)
			self.process_filtered(need_to_parse)

		elif self.command == "auto":
			obj = self.read_auto()
			assigns = self.read_nested_assigns()
			self.engine.auto(obj, assigns)

		elif self.command == "print":
			obj = self.read_print()
			self.engine.print(obj)

		else:
			obj = self.read_assign()
			self.engine.assign(obj)

	def read_rule(self):
		rule = self.read_identifier()
		self.read_eol()
		return rule

	def read_build(self):
		self.expect_token()
		targets_explicit = []
		targets_implicit = []
		inputs_explicit = []
		inputs_implicit = []
		inputs_order = []

		# read targets explicit
		while self.line_stripped[0] not in ["|", ":"]:
			targets_explicit.append(self.read_path())
			self.expect_token()

		# read targets implicit
		if self.line_stripped[0] == "|":
			self.line_stripped = self.line_stripped[1:].strip()
			self.expect_token()
			while self.line_stripped[0] != ":":
				targets_implicit.append(self.read_path())
				self.expect_token()

		# read rule name
		self.expect_token(":")
		self.line_stripped = self.line_stripped[1:].strip()
		rule = self.read_identifier()

		if self.line_stripped:
			# read inputs explicit
			while self.line_stripped and (self.line_stripped[0] != "|"):
				inputs_explicit.append(self.read_path())

			# read inputs implicit
			if (len(self.line_stripped) >= 2) and (self.line_stripped[0] == "|") and (self.line_stripped[1] != "|"):
				self.line_stripped = self.line_stripped[1:].strip()
				while self.line_stripped and (self.line_stripped[0] != "|"):
					inputs_implicit.append(self.read_path())

			# read inputs order
			if self.line_stripped and (self.line_stripped[0] == "|") and (self.line_stripped[1] == "|"):
				self.line_stripped = self.line_stripped[2:].strip()
				while self.line_stripped:
					inputs_order.append(self.read_path())

		self.read_eol()
		return (
			self.from_esc(targets_explicit),
			self.from_esc(targets_implicit),
			rule,
			self.from_esc(inputs_explicit),
			self.from_esc(inputs_implicit),
			self.from_esc(inputs_order)
		)

	def read_default(self):
		self.expect_token()
		paths = []
		while self.line_stripped:
			paths.append(self.read_path())
		self.read_eol()
		return self.from_esc(paths)

	def read_pool(self):
		pool = self.read_identifier()
		self.read_eol()
		return pool

	def read_include(self):
		return self.read_one_path()

	def read_subninja(self):
		return self.read_one_path()

	def read_one_path(self):
		path = self.read_path()
		self.read_eol()
		return self.from_esc(path)

	def read_filter(self):
		self.expect_token()
		filters = []
		while self.line_stripped:
			name = self.read_identifier()
			self.expect_token(":")
			self.line_stripped = self.line_stripped[1:].strip()
			value = self.read_path()
			filters.append((name, self.from_esc(value)))
		self.read_eol()
		return filters

	def process_filtered(self, need_to_parse):
		ws_ref = self.whitespace
		while self.line_i < len(self.lines):
			start_i = self.line_i
			if not self.next_line(preserve_comments = need_to_parse):
				break
			# if offset is less then two spaces
			# then we stop processing
			if self.whitespace <= ws_ref + 1:
				self.line_i = start_i
				break
			if need_to_parse: # if we know that filter is disabled, no need to parse then
				self.parse_line()

	def read_auto(self):
		self.expect_token()
		targets = []
		inputs = []

		# read targets
		while self.line_stripped[0] != ":":
			targets.append(self.read_path())
			self.expect_token()

		# read rule name
		self.expect_token(":")
		self.line_stripped = self.line_stripped[1:].strip()
		rule = self.read_identifier()

		# read inputs
		self.expect_token()
		while self.line_stripped:
			inputs.append(self.read_path())
		self.read_eol()
		return (self.from_esc(targets), rule, self.from_esc(inputs))

	def read_print(self):
		return self.line_stripped.strip()

	def read_assign(self):
		self.expect_token("=")
		value = self.line_stripped[1:].strip()
		return (self.command, value)

	def read_nested_assigns(self):
		all = []
		while self.next_nested():
			all.append(self.read_nested_assign())
		return all

	def read_nested_assign(self):
		name = self.read_identifier()
		if name in keywords:
			raise ValueError("unexpected keyword token '%s' in '%s' (%s:%i)" % (
				name,
				self.line,
				self.filename,
				self.line_num
			))
		self.expect_token("=")
		value = self.line_stripped[1:].strip()
		return (name, value)

	def read_identifier(self):
		identifier = re_identifier.match(self.line_stripped)
		if not identifier:
			raise ValueError("expected token 'identifier' in '%s' (%s:%i)" % (
				self.line_stripped,
				self.filename,
				self.line_num
			))
		self.line_stripped = self.line_stripped[identifier.span()[1]:].strip()
		return identifier.group()

	def expect_token(self, name = ""):
		if name:
			if (not self.line_stripped) or (not self.line_stripped.startswith(name)):
				raise ValueError("expected token '%s' in '%s' (%s:%i)" % (
					name,
					self.line_stripped,
					self.filename,
					self.line_num
				))
		else:
			if not self.line_stripped:
				raise ValueError("expected token(s) in '%s' (%s:%i)" % (
					self.line_stripped,
					self.filename,
					self.line_num
				))

	def read_path(self):
		path = re_path.match(self.line_stripped)
		if not path:
			raise ValueError("expected token 'path' in '%s' (%s:%i)" % (
				self.line_stripped,
				self.filename,
				self.line_num
			))
		self.line_stripped = self.line_stripped[path.span()[1]:].strip()
		return path.group()

	def read_eol(self):
		if self.line_stripped:
			raise ValueError("unexpected token '%s' in '%s' (%s:%i)" % (
				self.line_stripped,
				self.line,
				self.filename,
				self.line_num
			))

	# try to read next nested line, roll-back if not successful
	def next_nested(self):
		start_i = self.line_i
		ws_ref = self.whitespace
		comments_len = len(self.comments)
		if not self.next_line():
			self.whitespace_nested = None
			return False
		if not self.whitespace_nested:
			if self.whitespace > ws_ref + 1: # at least two spaces
				self.whitespace_nested = self.whitespace
				return True
			else:
				self.line_i = start_i
				self.comments = self.comments[:comments_len]
				return False
		else:
			if self.whitespace == self.whitespace_nested:
				return True
			else:
				self.line_i = start_i
				self.whitespace_nested = None
				self.comments = self.comments[:comments_len]
				return False

	def next_line(self, preserve_comments = True):
		if self.line_i >= len(self.lines):
			return False

		self.line_stripped = ""
		while (not self.line_stripped) and (self.line_i < len(self.lines)):
			self.line = ""
			self.line_num = self.line_i + 1

			# dealing with escaped newlines
			newline_escaped = True
			while newline_escaped and (self.line_i < len(self.lines)):
				self.line += self.lines[self.line_i]
				self.line_i += 1
				newline_escaped = re_newline_escaped.search(self.line)
				if newline_escaped:
					l, r = newline_escaped.span()
					# in some cases we can have $$, $$$$, etc in the end
					# which are escaped $ combinations, and they don't escape newline
					if (r - l) % 2:
						# in case if they do $, $$$, etc, we need to strip last one
						self.line = self.line[:-1]
					else:
						newline_escaped = None

			# line is ready for processing
			self.line_stripped = self.line.strip()

			# skip empty lines
			if not self.line_stripped:
				continue

			# fast strip comment
			if self.line_stripped and self.line_stripped[0] == "#":
				if preserve_comments:
					self.comments.append(self.line_stripped[1:])
				self.line_stripped = ""
				continue

			# slower strip comments
			comment_eol = re_comment.search(self.line_stripped)
			if comment_eol:
				if preserve_comments:
					self.comments.append(comment_eol.group(1))
				self.line_stripped = self.line_stripped[:comment_eol.span()[0]].strip()

		# if we can't skip empty lines, than just return failure
		if not self.line_stripped:
			return False

		# get whitespace
		self.whitespace = self.line[:self.line.index(self.line_stripped)]
		self.whitespace = self.whitespace.replace("\t", "    ")
		self.whitespace = len(self.whitespace)
		return True

	def from_esc(self, value):
		if value == None:
			return None
		elif type(value) is str:
			if value.startswith("r\""):
				return value
			else:
				return value.replace("$\n", "").replace("$ ", " ").replace("$:", ":").replace("$$", "$")
		else:
			return [self.from_esc(str) for str in value]

# ----------------------------------------------------------- fox engine

class Engine:
	class Context:
		def __init__(self):
			# key is folder name, value is set of file names
			self.generated = collections.defaultdict(set)
			# number of generated subninja files
			self.subninja_num = 0

	def __init__(self, parent = None):
		if not parent:
			self.variables = {} # name: value
			self.auto_presets = {} # name: (inputs, outputs, assigns)
			self.rel_path = "" # this should be prepended to all parsed paths
			self.rules = {} # rule_name: {var_name: var_value}
			self.context = Engine.Context()
		else:
			self.variables = copy.copy(parent.variables)
			self.auto_presets = copy.copy(parent.auto_presets)
			self.rel_path = parent.rel_path
			self.rules = copy.copy(parent.rules)
			self.context = parent.context
		self.output = []
		self.need_eval = False
		self.filename = ""
		self.current_line = ""
		self.current_line_i = 0

	# load manifest
	def load(self, filename):
		self.filename = filename
		self.rel_path = self.rel_dir(filename)
		self.output.append("# generated with love by buildfox from %s" % filename)
		parser = Parser(self, filename)
		parser.parse()

	# load core definitions
	def load_core(self):
		self.filename = "fox_core.fox"
		self.rel_path = ""
		parser = Parser(self, self.filename, text = fox_core)
		parser.parse()

	# return output text
	def text(self):
		return "\n".join(self.output) + "\n"

	def save(self, filename):
		with open(filename, "w") as f:
			f.write(self.text())

	# return relative path to current work dir
	def rel_dir(self, filename):
		path = os.path.relpath(os.path.dirname(os.path.abspath(filename)), os.getcwd()).replace("\\", "/") + "/"
		if path == "./":
			path = ""
		return path

	def eval(self, text):
		def repl(matchobj):
			name = matchobj.group(1) or matchobj.group(2)
			if (name in self.variables) and (name not in self.visited_vars):
				self.need_eval = True
				self.visited_vars.add(name)
				return self.variables.get(name)
			else:
				return "${" + name + "}"
		self.need_eval = len(text) > 0
		self.visited_vars = set()
		while self.need_eval:
			self.need_eval = False
			text = re_var.sub(repl, text)
		return text

	# return regex value in filename is regex or wildcard
	def wildcard_regex(self, filename, output = False):
		if filename.startswith("r\""):
			return filename[2:-1] # strip r" and "
		elif "*" in filename or "?" in filename or "[" in filename:
			# based on fnmatch.translate with each wildcard is a capture group
			i, n = 0, len(filename)
			groups = 1
			res = ""
			while i < n:
				c = filename[i]
				i = i + 1
				if c == "*":
					if output:
						res = res + "\\" + str(groups)
						groups += 1
					else:
						res = res + "(.*)"
				elif c == "?":
					if output:
						res = res + "\\" + str(groups)
						groups += 1
					else:
						res = res + "(.)"
				elif output:
					res = res + c
				elif c == "[":
					j = i
					if j < n and filename[j] == "!":
						j = j + 1
					if j < n and filename[j] == "]":
						j = j + 1
					while j < n and filename[j] != "]":
						j = j + 1
					if j >= n:
						res = res + "\\["
					else:
						stuff = filename[i:j].replace("\\", "\\\\")
						i = j + 1
						if stuff[0] == "!":
							stuff = "^" + stuff[1:]
						elif stuff[0] == "^":
							stuff = "\\" + stuff
						res = "%s([%s])" % (res, stuff)
				else:
					res = res + re.escape(c)
			if output:
				return res
			else:
				return res + "\Z(?ms)"
		else:
			return None

	# input can be string or list of strings
	# outputs are always lists
	def eval_path(self, inputs, outputs = None):
		if inputs:
			result = []
			matched = []
			for input in inputs:
				input = self.eval(input)
				regex = self.wildcard_regex(input)
				if regex:
					# find the folder where to look for files
					base_folder = re_folder_part.match(regex)
					if base_folder:
						base_folder = base_folder.group()
						# rename regex back to readable form
						def replace_non_esc(match_group):
							return match_group.group(1)
						base_folder = re_non_escaped_char.sub(replace_non_esc, base_folder)
						separator = "\\" if base_folder.rfind("\\") > base_folder.rfind("/") else "/"
						base_folder = os.path.dirname(base_folder)
						list_folder = self.rel_path + base_folder
						
					else:
						separator = ""
						base_folder = ""
						if len(self.rel_path):
							list_folder = self.rel_path[:-1] # strip last /
						else:
							list_folder = "."

					# look for files
					list_folder = os.path.normpath(list_folder).replace("\\", "/")
					re_regex = re.compile(regex)
					if os.path.isdir(list_folder):
						fs_files = set(os.listdir(list_folder))
					else:
						fs_files = set()
					generated_files = self.context.generated.get(list_folder, set())
					for file in fs_files.union(generated_files):
						name = base_folder + separator + file
						match = re_regex.match(name)
						if match:
							result.append(self.rel_path + name)
							matched.append(match.groups())
				else:
					result.append(self.rel_path + input)
			inputs = result

		if outputs:
			result = []
			for output in outputs:
				output = self.eval(output)
				# we want \number instead of capture groups
				regex = self.wildcard_regex(output, True)
				if regex:
					for match in matched:
						# replace \number with data
						def replace_group(matchobj):
							index = int(matchobj.group(1)) - 1
							if index >= 0 and index < len(match):
								return match[index]
							else:
								return ""
						file = re_capture_group_ref.sub(replace_group, regex)
						result.append(self.rel_path + file)
				else:
					result.append(self.rel_path + output)

			# normalize results
			result = [os.path.normpath(file).replace("\\", "/") for file in result]

			# add them to generated files dict
			for file in result:
				dir = os.path.dirname(file)
				if dir == "":
					dir = "."
				name = os.path.basename(file)
				if name in self.context.generated[dir]:
					raise ValueError("two or more commands generate '%s' in '%s' (%s:%i)" % (
						file,
						self.current_line,
						self.filename,
						self.current_line_i,
					))
				else:
					self.context.generated[dir].add(name)

		# normalize inputs
		inputs = [os.path.normpath(file).replace("\\", "/") for file in inputs]

		if outputs:
			return inputs, result
		else:
			return inputs

	def eval_auto(self, inputs, outputs):
		for rule_name, auto in self.auto_presets.items(): # name: (inputs, outputs, assigns)
			# check if all inputs match required auto inputs
			for auto_input in auto[0]:
				regex = self.wildcard_regex(auto_input)
				if regex:
					re_regex = re.compile(regex)
					match = all(re_regex.match(input) for input in inputs)
				else:
					match = all(input == auto_input for input in inputs)
				if not match:
					break
			if not match:
				continue
			# check if all outputs match required auto outputs
			for auto_output in auto[1]:
				regex = self.wildcard_regex(auto_output)
				if regex:
					re_regex = re.compile(regex)
					match = all(re_regex.match(output) for output in outputs)
				else:
					match = all(output == auto_output for output in outputs)
				if not match:
					break
			if not match:
				continue
			# if everything match - return rule name and variables
			return rule_name, auto[2]
		# if no rule found then just fail and optionally return None 
		raise ValueError("unable to deduce auto rule in '%s' (%s:%i)" % (
			self.current_line,
			self.filename,
			self.current_line_i,
		))
		return None, None

	def eval_filter(self, name, regex_or_value):
		value = self.variables.get(name, "")
		regex = self.wildcard_regex(regex_or_value)
		if regex:
			return re.match(regex, value)
		else:
			return regex_or_value == value

	def write_assigns(self, assigns):
		for assign in assigns:
			name = self.eval(assign[0])
			value = self.eval(assign[1])
			self.output.append("  %s = %s" % (name, value))

	def comment(self, comment):
		self.output.append("#" + comment)

	def rule(self, obj, assigns):
		rule_name = self.eval(obj)
		self.output.append("rule " + rule_name)
		vars = {}
		for assign in assigns:
			name = assign[0]
			value = assign[1]
			vars[name] = value
			if name != "expand":
				self.output.append("  %s = %s" % (name, value))
		self.rules[rule_name] = vars

	def build(self, obj, assigns):
		inputs_explicit, targets_explicit = self.eval_path(obj[3], obj[0])
		targets_implicit = self.eval_path(obj[1])
		rule_name = self.eval(obj[2])
		inputs_implicit = self.eval_path(obj[4])
		inputs_order = self.eval_path(obj[5])

		# deduce auto rule
		if rule_name == "auto":
			name, vars = self.eval_auto(inputs_explicit, targets_explicit)
			rule_name = name
			assigns = vars + assigns

		# rule should exist
		if rule_name not in self.rules:
			raise ValueError("unknown rule %s at '%s' (%s:%i)" % (
				rule_name,
				self.current_line,
				self.filename,
				self.current_line_i,
			))

		# expand this rule
		expand = self.rules.get(rule_name).get("expand", None)

		if expand:
			# TODO probably this expand implementation is not enough

			if len(targets_explicit) != len(inputs_explicit):
				raise ValueError("cannot expand rule %s because of different amount of targets and inputs at '%s' (%s:%i)" % (
					rule_name,
					self.current_line,
					self.filename,
					self.current_line_i,
				))

			targets_explicit_indx = sorted(range(len(targets_explicit)), key = lambda k: targets_explicit[k])
			inputs_explicit_indx = sorted(range(len(inputs_explicit)), key = lambda k: inputs_explicit[k])
			targets_implicit = sorted(targets_implicit)
			inputs_implicit = sorted(inputs_implicit)
			inputs_order = sorted(inputs_order)

			for target_index in targets_explicit_indx:
				target = targets_explicit[target_index]
				input = inputs_explicit[target_index]

				self.output.append("build %s: %s %s%s%s" % (
					self.to_esc(target),
					rule_name,
					self.to_esc(input),
					" | " + " ".join(self.to_esc(inputs_implicit)) if inputs_implicit else "",
					" || " + " ".join(self.to_esc(inputs_order)) if inputs_order else "",
				))

				self.write_assigns(assigns)

			if targets_implicit: # TODO remove this when https://github.com/martine/ninja/pull/989 is merged
				self.output.append("build %s: phony %s" % (
					" ".join(self.to_esc(targets_implicit)),
					" ".join(self.to_esc(sorted(targets_explicit))),
				))
		else:
			# make generated output stable
			targets_explicit = sorted(targets_explicit)
			targets_implicit = sorted(targets_implicit)
			inputs_explicit = sorted(inputs_explicit)
			inputs_implicit = sorted(inputs_implicit)
			inputs_order = sorted(inputs_order)

			self.output.append("build %s: %s%s%s%s" % (
				" ".join(self.to_esc(targets_explicit)),
				rule_name,
				" " + " ".join(self.to_esc(inputs_explicit)) if inputs_explicit else "",
				" | " + " ".join(self.to_esc(inputs_implicit)) if inputs_implicit else "",
				" || " + " ".join(self.to_esc(inputs_order)) if inputs_order else "",
			))

			self.write_assigns(assigns)

			if targets_implicit: # TODO remove this when https://github.com/martine/ninja/pull/989 is merged
				self.output.append("build %s: phony %s" % (
					" ".join(self.to_esc(targets_implicit)),
					" ".join(self.to_esc(targets_explicit)),
				))

	def default(self, obj, assigns):
		paths = self.eval_path(obj)
		self.output.append("default " + " ".join(self.to_esc(paths)))
		self.write_assigns(assigns)

	def pool(self, obj, assigns):
		name = self.eval(obj)
		self.output.append("pool " + name)
		self.write_assigns(assigns)

	def filter(self, obj):
		for filt in obj:
			name = self.eval(filt[0])
			value = self.eval(filt[1])
			if not self.eval_filter(name, value):
				return False
		return True

	def auto(self, obj, assigns):
		outputs = [self.eval(output) for output in obj[0]] # this shouldn't be eval_path !
		name = self.eval(obj[1])
		inputs = [self.eval(input) for input in obj[2]] # this shouldn't be eval_path !
		self.auto_presets[name] = (inputs, outputs, assigns)

	def print(self, obj):
		print(self.eval(obj))

	def assign(self, obj):
		name = self.eval(obj[0])
		value = obj[1]
		self.variables[name] = value
		self.output.append("%s = %s" % (name, value))

	def include(self, obj):
		paths = self.eval_path([obj])
		for path in paths:
			old_rel_path = self.rel_path
			self.rel_path = self.rel_dir(path)
			parser = Parser(self, path)
			parser.parse()
			self.rel_path = old_rel_path

	def subninja(self, obj):
		paths = self.eval_path([obj])
		for path in paths:
			gen_filename = "__gen_%i_%s.ninja" % (
				self.context.subninja_num,
				re_alphanumeric.sub("", os.path.splitext(os.path.basename(path))[0])
			)
			self.context.subninja_num += 1
			engine = Engine(self)
			engine.load(path)
			engine.save(gen_filename)
			self.output.append("subninja " + self.to_esc(gen_filename))

	def to_esc(self, value):
		if value == None:
			return None
		elif type(value) is str:
			value = value.replace("$", "$$").replace(":", "$:").replace("\n", "$\n").replace(" ", "$ ")
			# escaping variables
			def repl(matchobj):
				return "${" + (matchobj.group(1) or matchobj.group(2)) + "}"
			return re_variable.sub(repl, value)
		else:
			return [self.to_esc(str) for str in value]

# ----------------------------------------------------------- environment

class Environment:
	def __init__(self):
		self.vars = {
			"variation": "debug"
		}

		if shutil.which("cl") and shutil.which("link") and shutil.which("lib"):
			self.vars["toolset_msvc"] = "true"
		if shutil.which("clang"):
			self.vars["toolset_clang"] = "true"
		if shutil.which("gcc") and shutil.which("g++"):
			self.vars["toolset_gcc"] = "true"

		if self.vars.get("toolset_msvc"):
			self.vars["toolset"] = "msvc"
		elif self.vars.get("toolset_clang"):
			self.vars["toolset"] = "clang"
		elif self.vars.get("toolset_gcc"):
			self.vars["toolset"] = "gcc"
		else:
			raise ValueError("cant find any compiler")

# ----------------------------------------------------------- processing

if args.get("workdir"):
	os.chdir(args.get("workdir"))

engine = Engine()

if args.get("env"):
	env = Environment()
	for name, value in env.vars.items():
		engine.assign((name, value))

for define in args.get("define"):
	engine.assign(define)

if args.get("core"):
	engine.load_core()

engine.load(args.get("in"))
engine.save(args.get("out"))
