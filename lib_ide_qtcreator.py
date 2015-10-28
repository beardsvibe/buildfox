# BuildFox ninja generator

from lib_ide_make import gen_make

qtcreator_ext_of_interest_src = (".c", ".cpp", ".cxx", ".c++", ".cc", ".h", ".hpp", ".hxx")

def gen_qtcreator(all_files, defines, includedirs, prj_name, buildfox_name):
	gen_make()

	all_files = ["%s%s" % ("" if folder == "./" else folder, name)
		for folder, names in all_files.items()
			for name in names
				if name.lower().endswith(qtcreator_ext_of_interest_src)]
	all_files = ["Makefile", buildfox_name] + all_files
	includedirs = ["."] + includedirs

	with open("%s.creator" % prj_name, "w") as f:
		f.write("[General]\n")
	with open("%s.config" % prj_name, "w") as f:
		f.write("%s\n" % "\n".join(["#define %s" % define for define in defines]))
	with open("%s.includes" % prj_name, "w") as f:
		f.write("%s\n" % "\n".join(includedirs))
	with open("%s.files" % prj_name, "w") as f:
		f.write("%s\n" % "\n".join(all_files))
