# BuildFox ninja generator

import os
import re
import sys
import shutil

re_folder_part = re.compile(r"(?:[^\r\n(\[\"\\]|\\.)+") # match folder part in filename regex
re_non_escaped_char = re.compile(r"(?<!\\)\\(.)") # looking for not escaped \ with char
re_capture_group_ref = re.compile(r"(?<!\\)\\(\d)") # match regex capture group reference

# return relative path to current work dir
def rel_dir(filename):
	path = os.path.relpath(os.path.dirname(os.path.abspath(filename)), os.getcwd()).replace("\\", "/") + "/"
	if path == "./":
		path = ""
	return path

# return regex value in filename for regex or wildcard
# replace_groups replace wildcards with group reference indexes
def wildcard_regex(filename, replace_groups = False):
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
				if replace_groups:
					res = res + "\\" + str(groups)
					groups += 1
				else:
					res = res + "(.*)"
			elif c == "?":
				if replace_groups:
					res = res + "\\" + str(groups)
					groups += 1
				else:
					res = res + "(.)"
			elif replace_groups:
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
		if replace_groups:
			return res
		else:
			return res + "\Z(?ms)"
	else:
		return None

# input can be string or list of strings
# outputs are always lists
def find_files(inputs, outputs = None, rel_path = "", generated = None):
	if inputs:
		result = []
		matched = []
		for input in inputs:
			regex = wildcard_regex(input)
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
					list_folder = rel_path + base_folder
					
				else:
					separator = ""
					base_folder = ""
					if len(rel_path):
						list_folder = rel_path[:-1] # strip last /
					else:
						list_folder = "."

				# look for files
				list_folder = os.path.normpath(list_folder).replace("\\", "/")
				re_regex = re.compile(regex)
				if os.path.isdir(list_folder):
					fs_files = set(os.listdir(list_folder))
				else:
					fs_files = set()
				generated_files = generated.get(list_folder, set())
				for file in fs_files.union(generated_files):
					name = base_folder + separator + file
					match = re_regex.match(name)
					if match:
						result.append(rel_path + name)
						matched.append(match.groups())
			else:
				result.append(rel_path + input)
		inputs = result

	if outputs:
		result = []
		for output in outputs:
			# we want \number instead of capture groups
			regex = wildcard_regex(output, True)
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
					result.append(rel_path + file)
			else:
				result.append(rel_path + output)

		# normalize results
		result = [os.path.normpath(file).replace("\\", "/") for file in result]

	# normalize inputs
	inputs = [os.path.normpath(file).replace("\\", "/") for file in inputs]

	inputs = sorted(inputs)
	if outputs:
		result = sorted(result)
	#targets_explicit_indx = sorted(range(len(targets_explicit)), key = lambda k: targets_explicit[k])
	#inputs_explicit_indx = sorted(range(len(inputs_explicit)), key = lambda k: inputs_explicit[k])

	if outputs:
		return inputs, result
	else:
		return inputs

# finds the file in path
def which(cmd, mode = os.F_OK | os.X_OK, path = None):
	if sys.version_info[0:2] >= (3, 3):
		return shutil.which(cmd, mode, path)
	else:
		def _access_check(fn, mode):
			return (os.path.exists(fn) and os.access(fn, mode)
					and not os.path.isdir(fn))

		if os.path.dirname(cmd):
			if _access_check(cmd, mode):
				return cmd
			return None

		if path is None:
			path = os.environ.get("PATH", os.defpath)
		if not path:
			return None
		path = path.split(os.pathsep)

		if sys.platform == "win32":
			if not os.curdir in path:
				path.insert(0, os.curdir)
			pathext = os.environ.get("PATHEXT", "").split(os.pathsep)
			if any(cmd.lower().endswith(ext.lower()) for ext in pathext):
				files = [cmd]
			else:
				files = [cmd + ext for ext in pathext]
		else:
			files = [cmd]

		seen = set()
		for dir in path:
			normdir = os.path.normcase(dir)
			if not normdir in seen:
				seen.add(normdir)
				for thefile in files:
					name = os.path.join(dir, thefile)
					if _access_check(name, mode):
						return name
		return None
