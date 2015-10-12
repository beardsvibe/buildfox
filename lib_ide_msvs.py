# BuildFox ninja generator

from pprint import pprint

ext_of_interest = (".c", ".cpp", ".cxx", ".c++", ".cc", ".h", ".hpp", ".hxx")

def gen_msvs(all_files):
	# filter files of interest
	interest_files = {}
	for folder, files in all_files.items():
		interest = set()
		for name in files:
			if name.lower().endswith(ext_of_interest):
				interest.add(name)
		if interest:
			interest_files[folder] = interest

	pprint(interest_files)

# OLD MASK CODE

#import os
#import shutil
#import uuid
#from lib.tool_classic_tree import to_trees
#
## TODO
#def is_source(name):
#	return name.lower().endswith((".c", ".cpp", ".cxx", ".cc", ".h", ".hpp", ".hxx"))
#
#def gen_uuid():
#	return "{{{0}}}".format(str(uuid.uuid4()).upper())
#
#def gen_uuid_from(s):
#	return "{{{0}}}".format(str(uuid.uuid5(uuid.NAMESPACE_URL, s)).upper())
#
#def generate_solution(projects):
#	output = "Microsoft Visual Studio Solution File, Format Version 13.00" + "\n"
#	output += "# Visual Studio 2013" + "\n"
#
#	for project in projects:
#		name = project["name"]
#		guid = project["guid"]
#		# This guid is a project type.
#		output += "Project(\"{{8BC9CEB8-8B4A-11D0-8D11-00A0C91BC942}}\") = \"{0}\", \"{0}.vcxproj\", \"{1}\"".format(name, guid) + "\n"
#
#	output += "Global" + "\n"
#	output += "	GlobalSection(SolutionProperties) = preSolution" + "\n"
#	output += "		HideSolutionNode = FALSE" + "\n"
#	output += "	EndGlobalSection" + "\n"
#	output += "EndGlobal" + "\n"
#	return output
#
#def relative_to_root(file_path):
#	return os.path.relpath(file_path)
#
#def generate_project(project, root):
#	name = project["name"]
#	guid = project["guid"]
#	files = project["files"]
#
#	project_file  = '<?xml version="1.0" encoding="utf-8"?>' + "\n"
#	project_file += '<Project DefaultTargets="Build" ToolsVersion="4.0" xmlns="http://schemas.microsoft.com/developer/msbuild/2003">' + "\n"
#
#	### Project configurations.
#	project_file += '	<ItemGroup Label="ProjectConfigurations">' + "\n"
#	project_file += '		<ProjectConfiguration Include="Debug|Win32">' + "\n"
#	project_file += '			<Configuration>Debug</Configuration>' + "\n"
#	project_file += '			<Platform>Win32</Platform>' + "\n"
#	project_file += '		</ProjectConfiguration>' + "\n"
#	project_file += '		<ProjectConfiguration Include="Release|Win32">' + "\n"
#	project_file += '			<Configuration>Release</Configuration>' + "\n"
#	project_file += '			<Platform>Win32</Platform>' + "\n"
#	project_file += '		</ProjectConfiguration>' + "\n"
#	project_file += '	</ItemGroup>' + "\n"
#	project_file += '	<PropertyGroup Label="Globals">' + "\n"
#	project_file += '		<ProjectName>{0}</ProjectName>'.format(name) + "\n"
#	project_file += '		<ProjectGuid>{0}</ProjectGuid>'.format(guid) + "\n"
#	project_file += '	</PropertyGroup>' + "\n"
#	project_file += '	<Import Project="$(VCTargetsPath)\Microsoft.Cpp.Default.props" />' + "\n"
#
#	### Configurations' toolset options.
#	#ConfigurationType :
#	#	Application			Application (.exe)
#	#	DynamicLibrary		Dynamic Library (.dll)
#	#	Generic				Makefile, displays makefile toolset (NMake)
#	#	StaticLibrary		Static Library (.dll)
#	#	Unknown				Utility
#	
#	#CharacterSet
#	#	NotSet
#	#	Unicode
#	#	MBCS
#
#	project_file += '	<PropertyGroup Condition="\'$(Configuration)|$(Platform)\'==\'Debug|Win32\'" Label="Configuration">' + "\n"
#	project_file += '		<ConfigurationType>Application</ConfigurationType>' + "\n"
#	project_file += '		<UseDebugLibraries>true</UseDebugLibraries>' + "\n"
#	project_file += '		<PlatformToolset>v120</PlatformToolset>' + "\n"
#	project_file += '		<CharacterSet>Unicode</CharacterSet>' + "\n"
#	project_file += '	</PropertyGroup>' + "\n"
#
#	project_file += '	<PropertyGroup Condition="\'$(Configuration)|$(Platform)\'==\'Release|Win32\'" Label="Configuration">' + "\n"
#	project_file += '		<ConfigurationType>Application</ConfigurationType>' + "\n"
#	project_file += '		<UseDebugLibraries>false</UseDebugLibraries>' + "\n"
#	project_file += '		<PlatformToolset>v120</PlatformToolset>' + "\n"
#	project_file += '		<WholeProgramOptimization>true</WholeProgramOptimization>' + "\n"
#	project_file += '		<CharacterSet>Unicode</CharacterSet>' + "\n"
#	project_file += '	</PropertyGroup>' + "\n"
#
#	project_file += '	<Import Project="$(VCTargetsPath)\Microsoft.Cpp.props" />' + "\n"
#	project_file += '	<ImportGroup Label="ExtensionSettings">' + "\n"
#	project_file += '	</ImportGroup>' + "\n"
#
#	project_file += '	<ImportGroup Label="PropertySheets" Condition="\'$(Configuration)|$(Platform)\'==\'Debug|Win32\'">' + "\n"
#	project_file += '		<Import Project="$(UserRootDir)\Microsoft.Cpp.$(Platform).user.props" Condition="exists(\'$(UserRootDir)\Microsoft.Cpp.$(Platform).user.props\')" Label="LocalAppDataPlatform" />' + "\n"
#	project_file += '	</ImportGroup>' + "\n"
#	project_file += '	<ImportGroup Label="PropertySheets" Condition="\'$(Configuration)|$(Platform)\'==\'Release|Win32\'">' + "\n"
#	project_file += '		<Import Project="$(UserRootDir)\Microsoft.Cpp.$(Platform).user.props" Condition="exists(\'$(UserRootDir)\Microsoft.Cpp.$(Platform).user.props\')" Label="LocalAppDataPlatform" />' + "\n"
#	project_file += '	</ImportGroup>' + "\n"
#
#	project_file += '	<PropertyGroup Label="UserMacros" />' + "\n"
#	project_file += '	<PropertyGroup Condition="\'$(Configuration)|$(Platform)\'==\'Debug|Win32\'">' + "\n"
#	project_file += '		<LinkIncremental>true</LinkIncremental>' + "\n"
#	project_file += '	</PropertyGroup>' + "\n"
#	project_file += '	<PropertyGroup Condition="\'$(Configuration)|$(Platform)\'==\'Release|Win32\'">' + "\n"
#	project_file += '		<LinkIncremental>false</LinkIncremental>' + "\n"
#	project_file += '	</PropertyGroup>' + "\n"
#
#	### Configurations' compiler options.
#	project_file += '	<ItemDefinitionGroup Condition="\'$(Configuration)|$(Platform)\'==\'Debug|Win32\'">' + "\n"
#	project_file += '		<ClCompile>' + "\n"
#	project_file += '			<PrecompiledHeader>' + "\n"
#	project_file += '			</PrecompiledHeader>' + "\n"
#	project_file += '			<WarningLevel>Level3</WarningLevel>' + "\n"
#	project_file += '			<Optimization>Disabled</Optimization>' + "\n"
#	project_file += '			<PreprocessorDefinitions>WIN32;_DEBUG;_WINDOWS;%(PreprocessorDefinitions)</PreprocessorDefinitions>' + "\n"
#	project_file += '		</ClCompile>' + "\n"
#	project_file += '		<Link>' + "\n"
#	project_file += '			<SubSystem>Windows</SubSystem>' + "\n"
#	project_file += '			<GenerateDebugInformation>true</GenerateDebugInformation>' + "\n"
#	project_file += '		</Link>' + "\n"
#	project_file += '	</ItemDefinitionGroup>' + "\n"
#
#	project_file += '	<ItemDefinitionGroup Condition="\'$(Configuration)|$(Platform)\'==\'Release|Win32\'">' + "\n"
#	project_file += '		<ClCompile>' + "\n"
#	project_file += '			<WarningLevel>Level3</WarningLevel>' + "\n"
#	project_file += '			<PrecompiledHeader>' + "\n"
#	project_file += '			</PrecompiledHeader>' + "\n"
#	project_file += '			<Optimization>MaxSpeed</Optimization>' + "\n"
#	project_file += '			<FunctionLevelLinking>true</FunctionLevelLinking>' + "\n"
#	project_file += '			<IntrinsicFunctions>true</IntrinsicFunctions>' + "\n"
#	project_file += '			<PreprocessorDefinitions>WIN32;NDEBUG;_WINDOWS;%(PreprocessorDefinitions)</PreprocessorDefinitions>' + "\n"
#	project_file += '		</ClCompile>' + "\n"
#	project_file += '		<Link>' + "\n"
#	project_file += '			<SubSystem>Windows</SubSystem>' + "\n"
#	project_file += '			<GenerateDebugInformation>true</GenerateDebugInformation>' + "\n"
#	project_file += '			<EnableCOMDATFolding>true</EnableCOMDATFolding>' + "\n"
#	project_file += '			<OptimizeReferences>true</OptimizeReferences>' + "\n"
#	project_file += '		</Link>' + "\n"
#	project_file += '	</ItemDefinitionGroup>' + "\n"
#
#	# Files to build.
#	project_file += '	<ItemGroup>' + "\n"
#	for file in files:
#		relative_path = relative_to_root(file)
#		if is_source(file):
#			project_file += '		<ClCompile Include="{0}" />'.format(relative_path) + "\n"
#		else:
#			project_file += '		<ClInclude Include="{0}" />'.format(relative_path) + "\n"
#	project_file += '	</ItemGroup>' + "\n"
#
#	project_file += '	<Import Project="$(VCTargetsPath)\Microsoft.Cpp.targets" />' + "\n"
#	project_file += '	<ImportGroup Label="ExtensionTargets">' + "\n"
#	project_file += '	</ImportGroup>' + "\n"
#	project_file += '</Project>' + "\n"
#
#	return project_file
#
#def parent_dir_of(path):
#	parents = []
#
#	path = os.path.dirname(path)
#	while path not in ['.', '/', '\\', 'C:\\', 'C:/', '']:
#		parents.append(path)
#		path = os.path.dirname(path)
#
#	return list(reversed(parents))
#
## Is it for real, that python lacks this?
#def flatten(_list):
#	return sum(([x] if not isinstance(x, list) else flatten(x) for x in _list), [])
#
#def generate_directories(files):
#	return sorted(list(set(flatten([parent_dir_of(f) for f in files]))))
#
#def generate_project_filters(project, root):
#	files = project["files"]
#
#	filters  = '<?xml version="1.0" encoding="utf-8"?>' + "\n"
#	filters += '<Project ToolsVersion="4.0" xmlns="http://schemas.microsoft.com/developer/msbuild/2003">' + "\n"
#
#	filters += '	<ItemGroup>' + "\n"
#	for dir in generate_directories(files):
#		dir = dir.replace("/", "\\")
#		dir_guid = gen_uuid_from(dir).lower()
#
#		filters += '		<Filter Include="{0}">'.format(dir) + "\n"
#		filters += '			<UniqueIdentifier>{0}></UniqueIdentifier>'.format(dir_guid) + "\n"
#		filters += '		</Filter>' + "\n"
#	filters += '	</ItemGroup>' + "\n"
#
#	filters += '	<ItemGroup>' + "\n"
#	for file in files:
#		file = file.replace("/", "\\")
#		file_path = relative_to_root(file)
#		filter_path = os.path.dirname(file)
#
#		if is_source(file):
#			filters += '		<ClCompile Include="{0}">'.format(file_path) + "\n"
#			filters += '			<Filter>{0}</Filter>'.format(filter_path) + "\n"
#			filters += '		</ClCompile>' + "\n"
#		else:
#			filters += '		<ClInclude Include="{0}">'.format(file_path) + "\n"
#			filters += '			<Filter>{0}</Filter>'.format(filter_path) + "\n"
#			filters += '		</ClInclude>' + "\n"
#	filters += '	</ItemGroup>' + "\n"
#
#	filters += '</Project>' + "\n"
#
#	return filters
#
#def to_file(filename_sln, ir, args = None):
#	root = os.path.dirname(filename_sln)
#	final_projects = [
#		#{ "name": "application", "guid": gen_uuid(), "files": ["app/main.cpp", "app/test_folder/nested.cpp"] },
#		#{ "name": "tests", "guid": gen_uuid(), "files": ["tests/string-tests.cpp", "tests/vector-tests.cpp"] }
#	]
#
#	# TODO merge different build trees for different variation
#	for tree in to_trees(ir):
#		final_projects.append({
#			"name": tree.prj_name + "_" + tree.variation_name + "_" + tree.end_target.target,
#			"guid": gen_uuid(),
#			"files": [os.path.relpath(src.target, root) for src in tree.source_targets]
#			# TODO add compiler flags !
#		})
#
#	#print("Projects for final generation :")
#	#from pprint import pprint
#	#pprint(final_projects)
#
#	with open(filename_sln, "w") as f:
#		f.write(generate_solution(final_projects))
#
#	for project in final_projects:
#		project_content = generate_project(project, root)
#		filters_content = generate_project_filters(project, root)
#		with open(os.path.join(root, "{0}.vcxproj".format(project["name"])), "w") as f:
#			f.write(project_content)
#		with open(os.path.join(root, "{0}.vcxproj.filters".format(project["name"])), "w") as f:
#			f.write(filters_content)
#
#

# template vcxproj
#
#<?xml version="1.0" encoding="utf-8"?>
#<Project DefaultTargets="Build" ToolsVersion="12.0" xmlns="http://schemas.microsoft.com/developer/msbuild/2003">
#  <ItemGroup Label="ProjectConfigurations">
#    <ProjectConfiguration Include="Debug|Win32">
#      <Configuration>Debug</Configuration>
#      <Platform>Win32</Platform>
#    </ProjectConfiguration>
#    <ProjectConfiguration Include="Release|Win32">
#      <Configuration>Release</Configuration>
#      <Platform>Win32</Platform>
#    </ProjectConfiguration>
#  </ItemGroup>
#  <PropertyGroup Label="Globals">
#    <ProjectGuid>{A5975D75-ACD0-4CB9-BE5B-A1EA61108AA5}</ProjectGuid>
#    <Keyword>MakeFileProj</Keyword>
#  </PropertyGroup>
#  <Import Project="$(VCTargetsPath)\Microsoft.Cpp.Default.props" />
#  <PropertyGroup Condition="'$(Configuration)|$(Platform)'=='Debug|Win32'" Label="Configuration">
#    <ConfigurationType>Makefile</ConfigurationType>
#    <UseDebugLibraries>true</UseDebugLibraries>
#    <PlatformToolset>v120</PlatformToolset>
#  </PropertyGroup>
#  <PropertyGroup Condition="'$(Configuration)|$(Platform)'=='Release|Win32'" Label="Configuration">
#    <ConfigurationType>Makefile</ConfigurationType>
#    <UseDebugLibraries>false</UseDebugLibraries>
#    <PlatformToolset>v120</PlatformToolset>
#  </PropertyGroup>
#  <Import Project="$(VCTargetsPath)\Microsoft.Cpp.props" />
#  <ImportGroup Label="ExtensionSettings">
#  </ImportGroup>
#  <ImportGroup Label="PropertySheets" Condition="'$(Configuration)|$(Platform)'=='Debug|Win32'">
#    <Import Project="$(UserRootDir)\Microsoft.Cpp.$(Platform).user.props" Condition="exists('$(UserRootDir)\Microsoft.Cpp.$(Platform).user.props')" Label="LocalAppDataPlatform" />
#  </ImportGroup>
#  <ImportGroup Label="PropertySheets" Condition="'$(Configuration)|$(Platform)'=='Release|Win32'">
#    <Import Project="$(UserRootDir)\Microsoft.Cpp.$(Platform).user.props" Condition="exists('$(UserRootDir)\Microsoft.Cpp.$(Platform).user.props')" Label="LocalAppDataPlatform" />
#  </ImportGroup>
#  <PropertyGroup Label="UserMacros" />
#  <PropertyGroup Condition="'$(Configuration)|$(Platform)'=='Debug|Win32'">
#    <NMakeBuildCommandLine>ninja</NMakeBuildCommandLine>
#    <NMakeOutput>test.exe</NMakeOutput>
#    <NMakeCleanCommandLine>ninja -t clean</NMakeCleanCommandLine>
#    <NMakeReBuildCommandLine>ninja -t clean &amp;&amp; ninja</NMakeReBuildCommandLine>
#    <NMakePreprocessorDefinitions>WIN32;_DEBUG;$(NMakePreprocessorDefinitions)</NMakePreprocessorDefinitions>
#  </PropertyGroup>
#  <PropertyGroup Condition="'$(Configuration)|$(Platform)'=='Release|Win32'">
#    <NMakeBuildCommandLine>ninja</NMakeBuildCommandLine>
#    <NMakeOutput>test.exe</NMakeOutput>
#    <NMakeCleanCommandLine>ninja -t clean</NMakeCleanCommandLine>
#    <NMakeReBuildCommandLine>ninja -t clean &amp;&amp; ninja</NMakeReBuildCommandLine>
#    <NMakePreprocessorDefinitions>WIN32;NDEBUG;$(NMakePreprocessorDefinitions)</NMakePreprocessorDefinitions>
#  </PropertyGroup>
#  <ItemDefinitionGroup>
#  </ItemDefinitionGroup>
#  <ItemGroup>
#    <Text Include="readme.txt" />
#  </ItemGroup>
#  <ItemGroup>
#    <ClCompile Include="main.cpp" />
#  </ItemGroup>
#  <Import Project="$(VCTargetsPath)\Microsoft.Cpp.targets" />
#  <ImportGroup Label="ExtensionTargets">
#  </ImportGroup>
#</Project>
#
# template vcxproj.filters
#
#<?xml version="1.0" encoding="utf-8"?>
#<Project ToolsVersion="4.0" xmlns="http://schemas.microsoft.com/developer/msbuild/2003">
#  <ItemGroup>
#    <Filter Include="Source Files">
#      <UniqueIdentifier>{4FC737F1-C7A5-4376-A066-2A32D752A2FF}</UniqueIdentifier>
#      <Extensions>cpp;c;cc;cxx;def;odl;idl;hpj;bat;asm;asmx</Extensions>
#    </Filter>
#    <Filter Include="Header Files">
#      <UniqueIdentifier>{93995380-89BD-4b04-88EB-625FBE52EBFB}</UniqueIdentifier>
#      <Extensions>h;hh;hpp;hxx;hm;inl;inc;xsd</Extensions>
#    </Filter>
#    <Filter Include="Resource Files">
#      <UniqueIdentifier>{67DA6AB6-F800-4c08-8B7A-83BB121AAD01}</UniqueIdentifier>
#      <Extensions>rc;ico;cur;bmp;dlg;rc2;rct;bin;rgs;gif;jpg;jpeg;jpe;resx;tiff;tif;png;wav;mfcribbon-ms</Extensions>
#    </Filter>
#  </ItemGroup>
#  <ItemGroup>
#    <Text Include="readme.txt" />
#  </ItemGroup>
#  <ItemGroup>
#    <ClCompile Include="main.cpp">
#      <Filter>Source Files</Filter>
#    </ClCompile>
#  </ItemGroup>
#</Project>