# BuildFox ninja generator

import os
import re
import sys
import shutil

re_folder_part = re.compile(r"^((?:\(\.\*\)\(\.\*\)|(?:[^\r\n(\[\"\\]|\\.))+)(\\\/|\/|\\).*$") # match folder part in filename regex
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

from pprint import pprint
# return list of folders that match provided pattern
# please note that some folders may point into non existing location
def glob_folders(pattern, rel_path = "", generated = None):
	real_folders = [rel_path if rel_path else "."]
	gen_folders = [rel_path if rel_path else "."]

	for folder in pattern.split("/"):
		if folder == "(.*)(.*)":
			new_real_folders = []
			for real_folder in real_folders:
				for root, dirnames, filenames in os.walk(real_folder): # TODO this is slow, optimize
					for dir in dirnames:
						result = os.path.join(root, dir).replace("\\", "/")
						new_real_folders.append(result)
			real_folders = new_real_folders

			new_gen_folders = []
			for gen_folder in gen_folders:
				prepend_dot = False
				if gen_folder.startswith("./"):
					prepend_dot = True
					gen_folder = gen_folder[2:] # strip ./
				gen_folder_len = len(gen_folder)
				for folder in generated.keys():
					if folder.startswith(gen_folder):
						root = folder[:gen_folder_len]
						sub_folders = folder[gen_folder_len:]
						sub_folders = sub_folders.lstrip("/")
						# walk through directories in similar fashion with os.walk
						new_gen_folders.append("./%s" % root if prepend_dot else root)
						for subfolder in sub_folders.split("/"): 
							root += "/%s" % subfolder
							new_gen_folders.append("./%s" % root if prepend_dot else root)
			gen_folders = list(set(new_gen_folders))
		else:
			real_folders = ["%s/%s" % (p, folder) for p in real_folders]
			gen_folders = ["%s/%s" % (p, folder) for p in gen_folders]

	return (real_folders, gen_folders)


# input can be string or list of strings
# outputs are always lists
def find_files(inputs, outputs = None, rel_path = "", generated = None):
	# rename regex back to readable form
	def replace_non_esc(match_group):
		return match_group.group(1)
	if inputs:
		result = []
		matched = []
		for input in inputs:
			regex = wildcard_regex(input)
			print("----------------------")
			#print("input %s" % input)
			#print("regex %s" % regex)
			if regex:
				# find the folder where to look for files
				base_folder = re_folder_part.match(regex)
				if base_folder:
					#print("matched %s" % str(base_folder))
					base_folder = base_folder.group(1) + base_folder.group(2)
					base_folder = re_non_escaped_char.sub(replace_non_esc, base_folder)
					#print("basefolder %s" % str(base_folder))
					separator = "\\" if base_folder.rfind("\\") > base_folder.rfind("/") else "/"
					base_folder = os.path.dirname(base_folder)
					list_folder = rel_path + base_folder
					#print("list_folder %s" % list_folder)
				else:
					separator = ""
					base_folder = ""
					if len(rel_path):
						list_folder = rel_path[:-1] # strip last /
					else:
						list_folder = "."

				# look for files
				list_folder = os.path.normpath(list_folder).replace("\\", "/")
				print("list_folder %s" % list_folder)
				
				all_listed_folders = glob_folders(list_folder, rel_path, generated)

				
				
				fs_files = set()
				generated_files = set()
				
				if False:
					#tmp_folders = ["."]
					print(" --> TODO")
					#
					#for folder in all_listed_folders:
					#	if folder == "(.*)(.*)":
					#		print(folder)
					#		pprint(tmp_folders)
					#		tmp_folders2 = []
					#		for tmp_folder in tmp_folders:
					#			print(tmp_folder)
					#			for root, dirnames, filenames in os.walk(tmp_folder):
					#				for dir in dirnames:
					#					tmp_folders2.append(os.path.join(root, dir).replace("\\", "/"))
					#					print(root + " === " + dir)
					#		# TODO filtering ?
					#		tmp_folders = tmp_folders2
					#		
					#	else:
					#		tmp_folders = [f + separator + folder for f in tmp_folders]
					#pprint(tmp_folders)
				else:
					if os.path.isdir(list_folder):
						fs_files = set(os.listdir(list_folder))
						fs_files = set([base_folder + separator + name for name in fs_files])

					generated_files = generated.get(list_folder, set())
					generated_files = set([base_folder + separator + name for name in generated_files])

				# we must have stable sort here
				# so output ninja files will be same between runs
				all_files = list(fs_files.union(generated_files))
				all_files = sorted(all_files)

				# while capturing ** we want just to capture *
				#if is_recursive_glob:
				#	regex = regex.replace("(.*)(.*)", "(.*)") # TODO check if this is correct

				#print("final regex : %s" % regex)

				re_regex = re.compile(regex)
				for file in all_files:
					name =  file
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
					file = re_non_escaped_char.sub(replace_non_esc, file)

					result.append(rel_path + file)
			else:
				result.append(rel_path + output)

		# normalize results
		result = [os.path.normpath(file).replace("\\", "/") for file in result]

	# normalize inputs
	inputs = [os.path.normpath(file).replace("\\", "/") for file in inputs]

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
