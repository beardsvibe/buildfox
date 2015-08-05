import os
import shutil
import uuid
from lib.tool_build_list import build_targets_dict, needed_to_execute_indexes, needed_to_execute_builds

def gen_uuid():
	return "{{{0}}}".format(str(uuid.uuid4()).upper())

def gen_uuid_from(s):
	return "{{{0}}}".format(str(uuid.uuid5(uuid.NAMESPACE_URL, s)).upper())

def generate_solution(projects):
	output = "Microsoft Visual Studio Solution File, Format Version 12.00" + "\n"
	output += "# Visual Studio 2012" + "\n"

	for project in projects:
		name = project["name"]
		guid = project["guid"]
		# This guid is a project type.
		output += "Project(\"{{8BC9CEB8-8B4A-11D0-8D11-00A0C91BC942}}\") = \"{0}\", \"{0}.vcxproj\", \"{1}\"".format(name, guid) + "\n"

	output += "Global" + "\n"
	output += "	GlobalSection(SolutionProperties) = preSolution" + "\n"
	output += "		HideSolutionNode = FALSE" + "\n"
	output += "	EndGlobalSection" + "\n"
	output += "EndGlobal" + "\n"
	return output

def relative_to_root(file_path):
	return os.path.relpath(file_path)

def generate_project(project, root):
	name = project["name"]
	guid = project["guid"]
	files = project["files"]

	project_file  = '<?xml version="1.0" encoding="utf-8"?>' + "\n"
	project_file += '<Project DefaultTargets="Build" ToolsVersion="4.0" xmlns="http://schemas.microsoft.com/developer/msbuild/2003">' + "\n"

	### Project configurations.
	project_file += '	<ItemGroup Label="ProjectConfigurations">' + "\n"
	project_file += '		<ProjectConfiguration Include="Debug|Win32">' + "\n"
	project_file += '			<Configuration>Debug</Configuration>' + "\n"
	project_file += '			<Platform>Win32</Platform>' + "\n"
	project_file += '		</ProjectConfiguration>' + "\n"
	project_file += '		<ProjectConfiguration Include="Release|Win32">' + "\n"
	project_file += '			<Configuration>Release</Configuration>' + "\n"
	project_file += '			<Platform>Win32</Platform>' + "\n"
	project_file += '		</ProjectConfiguration>' + "\n"
	project_file += '	</ItemGroup>' + "\n"
	project_file += '	<PropertyGroup Label="Globals">' + "\n"
	project_file += '		<ProjectName>{0}</ProjectName>'.format(name) + "\n"
	project_file += '		<ProjectGuid>{0}</ProjectGuid>'.format(guid) + "\n"
	project_file += '	</PropertyGroup>' + "\n"
	project_file += '	<Import Project="$(VCTargetsPath)\Microsoft.Cpp.Default.props" />' + "\n"

	### Configurations' toolset options.
	project_file += '	<PropertyGroup Condition="\'$(Configuration)|$(Platform)\'==\'Debug|Win32\'" Label="Configuration">' + "\n"
	project_file += '		<ConfigurationType>Application</ConfigurationType>' + "\n"
	project_file += '		<UseDebugLibraries>true</UseDebugLibraries>' + "\n"
	project_file += '		<PlatformToolset>v110</PlatformToolset>' + "\n"
	project_file += '		<CharacterSet>Unicode</CharacterSet>' + "\n"
	project_file += '	</PropertyGroup>' + "\n"

	project_file += '	<PropertyGroup Condition="\'$(Configuration)|$(Platform)\'==\'Release|Win32\'" Label="Configuration">' + "\n"
	project_file += '		<ConfigurationType>Application</ConfigurationType>' + "\n"
	project_file += '		<UseDebugLibraries>false</UseDebugLibraries>' + "\n"
	project_file += '		<PlatformToolset>v110</PlatformToolset>' + "\n"
	project_file += '		<WholeProgramOptimization>true</WholeProgramOptimization>' + "\n"
	project_file += '		<CharacterSet>Unicode</CharacterSet>' + "\n"
	project_file += '	</PropertyGroup>' + "\n"

	project_file += '	<Import Project="$(VCTargetsPath)\Microsoft.Cpp.props" />' + "\n"
	project_file += '	<ImportGroup Label="ExtensionSettings">' + "\n"
	project_file += '	</ImportGroup>' + "\n"

	project_file += '	<ImportGroup Label="PropertySheets" Condition="\'$(Configuration)|$(Platform)\'==\'Debug|Win32\'">' + "\n"
	project_file += '		<Import Project="$(UserRootDir)\Microsoft.Cpp.$(Platform).user.props" Condition="exists(\'$(UserRootDir)\Microsoft.Cpp.$(Platform).user.props\')" Label="LocalAppDataPlatform" />' + "\n"
	project_file += '	</ImportGroup>' + "\n"
	project_file += '	<ImportGroup Label="PropertySheets" Condition="\'$(Configuration)|$(Platform)\'==\'Release|Win32\'">' + "\n"
	project_file += '		<Import Project="$(UserRootDir)\Microsoft.Cpp.$(Platform).user.props" Condition="exists(\'$(UserRootDir)\Microsoft.Cpp.$(Platform).user.props\')" Label="LocalAppDataPlatform" />' + "\n"
	project_file += '	</ImportGroup>' + "\n"

	project_file += '	<PropertyGroup Label="UserMacros" />' + "\n"
	project_file += '	<PropertyGroup Condition="\'$(Configuration)|$(Platform)\'==\'Debug|Win32\'">' + "\n"
	project_file += '		<LinkIncremental>true</LinkIncremental>' + "\n"
	project_file += '	</PropertyGroup>' + "\n"
	project_file += '	<PropertyGroup Condition="\'$(Configuration)|$(Platform)\'==\'Release|Win32\'">' + "\n"
	project_file += '		<LinkIncremental>false</LinkIncremental>' + "\n"
	project_file += '	</PropertyGroup>' + "\n"

	### Configurations' compiler options.
	project_file += '	<ItemDefinitionGroup Condition="\'$(Configuration)|$(Platform)\'==\'Debug|Win32\'">' + "\n"
	project_file += '		<ClCompile>' + "\n"
	project_file += '			<PrecompiledHeader>' + "\n"
	project_file += '			</PrecompiledHeader>' + "\n"
	project_file += '			<WarningLevel>Level3</WarningLevel>' + "\n"
	project_file += '			<Optimization>Disabled</Optimization>' + "\n"
	project_file += '			<PreprocessorDefinitions>WIN32;_DEBUG;_WINDOWS;%(PreprocessorDefinitions)</PreprocessorDefinitions>' + "\n"
	project_file += '		</ClCompile>' + "\n"
	project_file += '		<Link>' + "\n"
	project_file += '			<SubSystem>Windows</SubSystem>' + "\n"
	project_file += '			<GenerateDebugInformation>true</GenerateDebugInformation>' + "\n"
	project_file += '		</Link>' + "\n"
	project_file += '	</ItemDefinitionGroup>' + "\n"

	project_file += '	<ItemDefinitionGroup Condition="\'$(Configuration)|$(Platform)\'==\'Release|Win32\'">' + "\n"
	project_file += '		<ClCompile>' + "\n"
	project_file += '			<WarningLevel>Level3</WarningLevel>' + "\n"
	project_file += '			<PrecompiledHeader>' + "\n"
	project_file += '			</PrecompiledHeader>' + "\n"
	project_file += '			<Optimization>MaxSpeed</Optimization>' + "\n"
	project_file += '			<FunctionLevelLinking>true</FunctionLevelLinking>' + "\n"
	project_file += '			<IntrinsicFunctions>true</IntrinsicFunctions>' + "\n"
	project_file += '			<PreprocessorDefinitions>WIN32;NDEBUG;_WINDOWS;%(PreprocessorDefinitions)</PreprocessorDefinitions>' + "\n"
	project_file += '		</ClCompile>' + "\n"
	project_file += '		<Link>' + "\n"
	project_file += '			<SubSystem>Windows</SubSystem>' + "\n"
	project_file += '			<GenerateDebugInformation>true</GenerateDebugInformation>' + "\n"
	project_file += '			<EnableCOMDATFolding>true</EnableCOMDATFolding>' + "\n"
	project_file += '			<OptimizeReferences>true</OptimizeReferences>' + "\n"
	project_file += '		</Link>' + "\n"
	project_file += '	</ItemDefinitionGroup>' + "\n"

	# Files to build.
	project_file += '	<ItemGroup>' + "\n"
	for file in files:
		relative_path = relative_to_root(file)
		project_file += '		<ClInclude Include="{0}" />'.format(relative_path) + "\n"
	project_file += '	</ItemGroup>' + "\n"

	project_file += '	<Import Project="$(VCTargetsPath)\Microsoft.Cpp.targets" />' + "\n"
	project_file += '	<ImportGroup Label="ExtensionTargets">' + "\n"
	project_file += '	</ImportGroup>' + "\n"
	project_file += '</Project>' + "\n"

	return project_file

def parent_dir_of(path):
	parents = []

	path = os.path.dirname(path)
	while path not in ['.', '/', '']:
		parents.append(path)
		path = os.path.dirname(path)

	return list(reversed(parents))

# Is it for real, that python lacks this?

def flatten(_list):
	return sum(([x] if not isinstance(x, list) else flatten(x) for x in _list), [])

def unique(_list):
	unique = []
	[unique.append(item) for item in _list if item not in unique]
	return unique

def generate_directories(files):
	return sorted(unique(flatten([parent_dir_of(f) for f in files])))

def generate_project_filters(project, root):
	files = project["files"]

	filters  = '<?xml version="1.0" encoding="utf-8"?>' + "\n"
	filters += '<Project ToolsVersion="4.0" xmlns="http://schemas.microsoft.com/developer/msbuild/2003">' + "\n"

	filters += '	<ItemGroup>' + "\n"
	for dir in generate_directories(files):
		dir = dir.replace("/", "\\")
		dir_guid = gen_uuid_from(dir).lower()

		filters += '		<Filter Include="{0}">'.format(dir) + "\n"
		filters += '			<UniqueIdentifier>{0}></UniqueIdentifier>'.format(dir_guid) + "\n"
		filters += '		</Filter>' + "\n"
	filters += '	</ItemGroup>' + "\n"

	filters += '	<ItemGroup>' + "\n"
	for file in files:
		file = file.replace("/", "\\")
		file_path = relative_to_root(file)
		filter_path = os.path.dirname(file)

		filters += '		<ClInclude Include="{0}">'.format(file_path) + "\n"
		filters += '			<Filter>{0}</Filter>'.format(filter_path) + "\n"
		filters += '		</ClInclude>' + "\n"
	filters += '	</ItemGroup>' + "\n"

	filters += '</Project>' + "\n"

	return filters

class MSVCToolchainCall:
	def __init__(self):
		pass

	def parse(self, command):
		pass

# simple helper for build target
class BuildTarget:
	def __init__(self, name, index, children):
		self.target = name
		self.build_index = index # number or None
		self.children = children # array of BuildTarget

	def is_exe_or_lib(self):
		return self.target.lower().endswith((".exe", ".lib", ".dll"))

	def is_obj(self):
		return self.target.lower().endswith(".obj")

	def is_source(self):
		return self.target.lower().endswith((".c", ".cpp", ".cxx", ".cc", ".h", ".hpp", ".hxx"))

	def __repr__(self):
		return self.target

# mask IR is not stricly a tree structure
# it's more like a graph (without cycles though)
# but msvc build structure is tree
# so this function convert ir graph to tree by cloning leafs
# all nodes on same level can be compiled in any order
def generate_generic_build_tree(target, readonly_ir, targets_dict):
	if target in targets_dict:
		index = targets_dict[target]
		children = []
		build = readonly_ir.builds[index]
		deps = set(build.inputs_explicit).union(build.inputs_implicit).union(build.inputs_order)
		for dep in deps:
			children.append(generate_generic_build_tree(dep, readonly_ir, targets_dict))
		return BuildTarget(target, index, children)
	else:
		return BuildTarget(target, None, [])

# abstraction for msvc build process :
# - prebuild step
# - compilation step (.cpp -> .obj)
# - linking step (.obj -> .exe)
# - postbuild step
class MSVCBuildTree:
	def __init__(self):
		self.objs_targets = [] # array of BuildTarget
		self.end_target = None # BuildTarget
		self.depends_on = [] # array of BuildTree
		self.pre_build = [] # array of BuildTarget
		self.post_build = [] # array of BuildTarget

	def __repr__(self):
		out = "buildtree :\n"
		out += "end target : %s\n" % self.end_target
		out += "objs targets : %s\n" % " ".join([str(v) for v in self.objs_targets])
		out += "depends on : %s\n" % " ".join([str(v) for v in self.depends_on])
		return out

	def figure_out_compiler_settings(self, readonly_ir):
		compiler_rules = {}
		for obj_target in self.objs_targets:
			rule = readonly_ir.rules[readonly_ir.builds[obj_target.build_index].rule]
			if rule.name not in compiler_rules:
				compiler_rules[rule.name] = rule

		print(compiler_rules)

		pass

	def figure_out_linker_settings(self, readonly_ir):
		pass

	def process_object(self, target):
		if target.is_obj():
			# create new target that only depends on sources
			new_target = BuildTarget(target.target, target.build_index, []);
			for child in target.children:
				if child.is_source():
					new_target.children.append(child)
				else:
					self.pre_build.append(child)

			if len(new_target.children) == 0:
				print("TODO obj doesn't not have any direct source inputs : " + target.target)

			if len(new_target.children) > 1:
				print("TODO warning more then one source for obj target : " + target.target)

			# append it to objects
			self.objs_targets.append(new_target)
		elif target.is_source():
			print("TODO direct cpp -> exe compilation")
		else:
			self.pre_build.append(child)

	def restore_from_root(self, target):
		if target.is_exe_or_lib():
			self.end_target = target
			for child in self.end_target.children:
				self.process_object(child)
			self.end_target.children = []
		else:
			# we need to put this is empty project with pre/post build step
			print("TODO not possible to build (dep project) " + str(target))

def to_file(filename_sln, readonly_ir, args = None):
	# get list of what we need to build
	targets_dict = build_targets_dict(readonly_ir)

	for prj_name, project in readonly_ir.projects.items():
		for variation_name, all_end_paths in project.variations.items():
			from pprint import pprint

			msvc_trees = []
			for target in all_end_paths:
				generic_tree = generate_generic_build_tree(target, readonly_ir, targets_dict)
				build_tree = MSVCBuildTree()
				build_tree.restore_from_root(generic_tree)
				build_tree.figure_out_compiler_settings(readonly_ir)
				build_tree.figure_out_linker_settings(readonly_ir)
				msvc_trees.append(build_tree)
		
			pprint(msvc_trees)

			# normal flow that msbuild provides :
			# c/cc/cpp -> obj -> exe/lib/dll

	#with open(filename, "w") as f:
	#	f.write(to_string(readonly_ir, variation))



### TEST
#root = "msvc-tests"
#if os.path.isdir(root):
#	shutil.rmtree(root)
#os.mkdir(root)
#os.chdir(root)
#
#projects = [
#	{ "name": "application", "guid": gen_uuid(), "files": ["app/main.cpp", "app/test_folder/nested.cpp"] },
#	{ "name": "tests", "guid": gen_uuid(), "files": ["tests/string-tests.cpp", "tests/vector-tests.cpp"] }
#]
#
#with open("test.sln", "w") as f:
#	f.write(generate_solution(projects))
#
#for project in projects:
#	project_content = generate_project(project, root)
#	filters_content = generate_project_filters(project, root)
#	with open("{0}.vcxproj".format(project["name"]), "w") as f:
#		f.write(project_content)
#	with open("{0}.vcxproj.filters".format(project["name"]), "w") as f:
#		f.write(filters_content)
#