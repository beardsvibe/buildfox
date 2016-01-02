# BuildFox ninja generator

import os
import uuid
from xml.sax import saxutils

vs_ext_of_interest_src = (".c", ".cpp", ".cxx", ".c++", ".cc", ".h", ".hpp", ".hxx")
vs_ext_of_interest_bin = (".exe")

vs_reference_sln = r"""Microsoft Visual Studio Solution File, Format Version %%%format_version%%%.00
# Visual Studio %%%studio_version%%%
Project("{8BC9CEB8-8B4A-11D0-8D11-00A0C91BC942}") = "%%%name%%%", "%%%file%%%", "%%%guid%%%"
EndProject
Global
	GlobalSection(SolutionProperties) = preSolution
		HideSolutionNode = FALSE
	EndGlobalSection
EndGlobal"""

vs_reference_prj = r"""<?xml version="1.0" encoding="utf-8"?>
<Project DefaultTargets="Build" ToolsVersion="%%%tools_version%%%.0" xmlns="http://schemas.microsoft.com/developer/msbuild/2003">
	<ItemGroup Label="ProjectConfigurations">
		<ProjectConfiguration Include="Debug|Win32">
			<Configuration>Debug</Configuration>
			<Platform>Win32</Platform>
		</ProjectConfiguration>
		<ProjectConfiguration Include="Release|Win32">
			<Configuration>Release</Configuration>
			<Platform>Win32</Platform>
		</ProjectConfiguration>
	</ItemGroup>
	<PropertyGroup Label="Globals">
		<ProjectName>%%%name%%%</ProjectName>
		<ProjectGuid>%%%guid%%%</ProjectGuid>
		<Keyword>MakeFileProj</Keyword>
	</PropertyGroup>
	<Import Project="$(VCTargetsPath)\Microsoft.Cpp.Default.props" />
	<PropertyGroup Condition="'$(Configuration)|$(Platform)'=='Debug|Win32'" Label="Configuration">
		<ConfigurationType>Makefile</ConfigurationType>
		<UseDebugLibraries>true</UseDebugLibraries>
		<PlatformToolset>v%%%platform_version%%%0</PlatformToolset>
	</PropertyGroup>
	<PropertyGroup Condition="'$(Configuration)|$(Platform)'=='Release|Win32'" Label="Configuration">
		<ConfigurationType>Makefile</ConfigurationType>
		<UseDebugLibraries>false</UseDebugLibraries>
		<PlatformToolset>v%%%platform_version%%%0</PlatformToolset>
	</PropertyGroup>
	<Import Project="$(VCTargetsPath)\Microsoft.Cpp.props" />
	<ImportGroup Label="ExtensionSettings">
	</ImportGroup>
	<ImportGroup Label="PropertySheets" Condition="'$(Configuration)|$(Platform)'=='Debug|Win32'">
		<Import Project="$(UserRootDir)\Microsoft.Cpp.$(Platform).user.props" Condition="exists('$(UserRootDir)\Microsoft.Cpp.$(Platform).user.props')" Label="LocalAppDataPlatform" />
	</ImportGroup>
	<ImportGroup Label="PropertySheets" Condition="'$(Configuration)|$(Platform)'=='Release|Win32'">
		<Import Project="$(UserRootDir)\Microsoft.Cpp.$(Platform).user.props" Condition="exists('$(UserRootDir)\Microsoft.Cpp.$(Platform).user.props')" Label="LocalAppDataPlatform" />
	</ImportGroup>
	<PropertyGroup Label="UserMacros" />
	<PropertyGroup Condition="'$(Configuration)|$(Platform)'=='Debug|Win32'">
		<NMakeBuildCommandLine>%%%nmake_build%%%</NMakeBuildCommandLine>
		<NMakeOutput>%%%output%%%</NMakeOutput>
		<NMakeCleanCommandLine>%%%nmake_clean%%%</NMakeCleanCommandLine>
		<NMakeReBuildCommandLine>%%%nmake_rebuild%%%</NMakeReBuildCommandLine>
		<NMakePreprocessorDefinitions>%%%defines%%%$(NMakePreprocessorDefinitions)</NMakePreprocessorDefinitions>
		<NMakeIncludeSearchPath>%%%includedirs%%%$(NMakeIncludeSearchPath)</NMakeIncludeSearchPath>
	</PropertyGroup>
	<PropertyGroup Condition="'$(Configuration)|$(Platform)'=='Release|Win32'">
		<NMakeBuildCommandLine>%%%nmake_build%%%</NMakeBuildCommandLine>
		<NMakeOutput>%%%output%%%</NMakeOutput>
		<NMakeCleanCommandLine>%%%nmake_clean%%%</NMakeCleanCommandLine>
		<NMakeReBuildCommandLine>%%%nmake_rebuild%%%</NMakeReBuildCommandLine>
		<NMakePreprocessorDefinitions>%%%defines%%%$(NMakePreprocessorDefinitions)</NMakePreprocessorDefinitions>
		<NMakeIncludeSearchPath>%%%includedirs%%%$(NMakeIncludeSearchPath)</NMakeIncludeSearchPath>
	</PropertyGroup>
	<ItemDefinitionGroup>
	</ItemDefinitionGroup>
	<ItemGroup>
%%%item_groups%%%
	</ItemGroup>
	<Import Project="$(VCTargetsPath)\Microsoft.Cpp.targets" />
	<ImportGroup Label="ExtensionTargets">
	</ImportGroup>
</Project>"""

vs_reference_flt = r"""<?xml version="1.0" encoding="utf-8"?>
<Project ToolsVersion="4.0" xmlns="http://schemas.microsoft.com/developer/msbuild/2003">
%%%items%%%
%%%filters%%%
</Project>"""

def gen_vs(all_files, defines, includedirs, prj_name, ide, cmd_env):
	interest_src_files = {}
	interest_bin_files = {}
	for folder, files in all_files.items():
		folder = os.path.abspath(folder).replace("/", "\\") + "\\"
		interest_src = set(filter(lambda n: n.lower().endswith(vs_ext_of_interest_src), files))
		interest_bin = set(filter(lambda n: n.lower().endswith(vs_ext_of_interest_bin), files))
		if interest_src:
			interest_src_files[folder] = interest_src
		if interest_bin:
			interest_bin_files[folder] = interest_bin

	output = ["%s%s" % (folder, name)
		for folder, files in interest_bin_files.items() for name in files]
	if len(output) > 1:
		print("more then one generated file is present, so we are choosing '%s' from all generated files :\n%s" % (output[0], "\n".join(output)))
	output = output[0]
	items = "\n".join(["		<ClCompile Include=\"%s%s\"/>" % (folder, name)
		for folder, files in interest_src_files.items() for name in files])

	defines = ";".join(defines) + ";" if defines else ""
	includedirs = ";".join(includedirs) + ";" if includedirs else ""

	# find common folder
	prefix = os.path.commonprefix([os.path.abspath(folder) for folder in interest_src_files.keys()])
	prefix = os.path.dirname(prefix)
	prefix_len = len(prefix)
	if prefix_len and prefix[-1] != "\\":
		prefix_len += 1 # and add slash to it

	flt_filters = []
	flt_items = []
	all_folder_filters = set()
	for folder in interest_src_files.keys():
		folder = folder[prefix_len:-1]
		path = None
		for subfolder in folder.split("\\"):
			path = "%s\\%s" % (path, subfolder) if path else subfolder
			all_folder_filters.add(path)

	for filter_path in all_folder_filters:
		folder_guid = "{%s}" % str(uuid.uuid5(uuid.NAMESPACE_URL, filter_path)).lower()
		filter_folder  = "		<Filter Include=\"%s\">\n" % filter_path
		filter_folder += "			<UniqueIdentifier>%s</UniqueIdentifier>\n" % folder_guid
		filter_folder += "		</Filter>"
		flt_filters.append(filter_folder)

	for folder, files in interest_src_files.items():
		filter_path = folder[prefix_len:-1]
		flt_items.append("\t<ItemGroup>")
		for name in files:
			item  = "		<ClCompile Include=\"%s%s\">\n" % (folder, name)
			item += "			<Filter>%s</Filter>\n" % filter_path
			item += "		</ClCompile>"
			flt_items.append(item)
		flt_items.append("\t</ItemGroup>")
	flt_filters = "\t<ItemGroup>\n%s\n\t</ItemGroup>\n" % "\n".join(flt_filters)
	flt_items = "\n".join(flt_items)

	cmd_env = cmd_env + " && " if cmd_env else ""

	toolset_ver = {
		"vs": "12",
		"vs2012": "4",
		"vs2013": "12",
		"vs2015": "14"
	}
	platform_ver = {
		"vs": "12",
		"vs2012": "11",
		"vs2013": "12",
		"vs2015": "14"
	}
	format_ver = {
		"vs": "13",
		"vs2012": "12",
		"vs2013": "13",
		"vs2015": "14"
	}
	studio_ver = {
		"vs": "2013",
		"vs2012": "2012",
		"vs2013": "2013",
		"vs2015": "2015"
	}

	prj_file = "%s.vcxproj" % prj_name
	prj_guid = "{%s}" % str(uuid.uuid4()).upper()
	prj_text = vs_reference_prj
	prj_text = prj_text.replace("%%%name%%%", prj_name)
	prj_text = prj_text.replace("%%%guid%%%", prj_guid)
	prj_text = prj_text.replace("%%%output%%%", output)
	prj_text = prj_text.replace("%%%defines%%%", defines)
	prj_text = prj_text.replace("%%%includedirs%%%", includedirs)
	prj_text = prj_text.replace("%%%item_groups%%%", items)
	prj_text = prj_text.replace("%%%tools_version%%%", toolset_ver.get(ide))
	prj_text = prj_text.replace("%%%platform_version%%%", platform_ver.get(ide))
	prj_text = prj_text.replace("%%%nmake_build%%%", saxutils.escape(cmd_env + "ninja"))
	prj_text = prj_text.replace("%%%nmake_clean%%%", saxutils.escape("ninja -t clean"))
	prj_text = prj_text.replace("%%%nmake_rebuild%%%", saxutils.escape(cmd_env + "ninja -t clean && ninja"))

	sln_file = "%s.sln" % prj_name
	sln_text = vs_reference_sln
	sln_text = sln_text.replace("%%%name%%%", prj_name)
	sln_text = sln_text.replace("%%%file%%%", prj_file)
	sln_text = sln_text.replace("%%%guid%%%", prj_guid)
	sln_text = sln_text.replace("%%%format_version%%%", format_ver.get(ide))
	sln_text = sln_text.replace("%%%studio_version%%%", studio_ver.get(ide))

	flt_file = "%s.vcxproj.filters" % prj_name
	flt_text = vs_reference_flt
	flt_text = flt_text.replace("%%%filters%%%", flt_filters)
	flt_text = flt_text.replace("%%%items%%%", flt_items)

	with open(prj_file, "w") as f:
		f.write(prj_text)
	with open(sln_file, "w") as f:
		f.write(sln_text)
	with open(flt_file, "w") as f:
		f.write(flt_text)
