# BuildFox ninja generator

from pprint import pprint
import os
import uuid

vs_ext_of_interest_src = (".c", ".cpp", ".cxx", ".c++", ".cc", ".h", ".hpp", ".hxx")
vs_ext_of_interest_bin = (".exe")

vs_reference_sln = r"""Microsoft Visual Studio Solution File, Format Version 13.00
# Visual Studio 2013
Project("{8BC9CEB8-8B4A-11D0-8D11-00A0C91BC942}") = "%%%name%%%", "%%%file%%%", "%%%guid%%%"
EndProject
Global
	GlobalSection(SolutionProperties) = preSolution
		HideSolutionNode = FALSE
	EndGlobalSection
EndGlobal"""

vs_reference_prj = r"""<?xml version="1.0" encoding="utf-8"?>
<Project DefaultTargets="Build" ToolsVersion="12.0" xmlns="http://schemas.microsoft.com/developer/msbuild/2003">
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
		<PlatformToolset>v120</PlatformToolset>
	</PropertyGroup>
	<PropertyGroup Condition="'$(Configuration)|$(Platform)'=='Release|Win32'" Label="Configuration">
		<ConfigurationType>Makefile</ConfigurationType>
		<UseDebugLibraries>false</UseDebugLibraries>
		<PlatformToolset>v120</PlatformToolset>
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
		<NMakeBuildCommandLine>ninja</NMakeBuildCommandLine>
		<NMakeOutput>%%%output%%%</NMakeOutput>
		<NMakeCleanCommandLine>ninja -t clean</NMakeCleanCommandLine>
		<NMakeReBuildCommandLine>ninja -t clean &amp;&amp; ninja</NMakeReBuildCommandLine>
		<NMakePreprocessorDefinitions>%%%defines%%%$(NMakePreprocessorDefinitions)</NMakePreprocessorDefinitions>
		<NMakeIncludeSearchPath>%%%includedirs%%%$(NMakeIncludeSearchPath)</NMakeIncludeSearchPath>
	</PropertyGroup>
	<PropertyGroup Condition="'$(Configuration)|$(Platform)'=='Release|Win32'">
		<NMakeBuildCommandLine>ninja</NMakeBuildCommandLine>
		<NMakeOutput>%%%output%%%</NMakeOutput>
		<NMakeCleanCommandLine>ninja -t clean</NMakeCleanCommandLine>
		<NMakeReBuildCommandLine>ninja -t clean &amp;&amp; ninja</NMakeReBuildCommandLine>
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
	<ItemGroup>
%%%filters%%%
	</ItemGroup>
	<ItemGroup>
%%%items%%%
	</ItemGroup>
</Project>"""

def gen_vs(all_files, defines, includedirs, prj_name):
	interest_src_files = {}
	interest_bin_files = {}
	for folder, files in all_files.items():
		folder = os.path.relpath(folder).replace("/", "\\") + "\\"
		interest_src = set(filter(lambda n: n.lower().endswith(vs_ext_of_interest_src), files))
		interest_bin = set(filter(lambda n: n.lower().endswith(vs_ext_of_interest_bin), files))
		if interest_src:
			interest_src_files[folder] = interest_src
		if interest_bin:
			interest_bin_files[folder] = interest_bin

	output = ", ".join(["%s%s" % (folder, name)
		for folder, files in interest_bin_files.items() for name in files])
	items = "\n".join(["		<ClCompile Include=\"%s%s\"/>" % (folder, name)
		for folder, files in interest_src_files.items() for name in files])

	defines = defines.replace("/D", "").replace(" ", ";") # this one is probably wrong
	if defines:
		defines += ";"

	includedirs = includedirs.replace("/I", "").replace(" ", ";") # this one is probably wrong
	if includedirs:
		includedirs += ";"

	flt_filters = []
	flt_items = []
	for folder, files in interest_src_files.items():
		if folder == ".\\":
			continue
		folder_guid = "{%s}" % str(uuid.uuid5(uuid.NAMESPACE_URL, folder)).lower()
		filter_folder  = "		<Filter Include=\"%s\">\n" % folder[:-1]
		filter_folder += "			<UniqueIdentifier>%s</UniqueIdentifier>\n" % folder_guid
		filter_folder += "		</Filter>"
		flt_filters.append(filter_folder)
		for name in files:
			item  = "		<ClCompile Include=\"%s%s\">\n" % (folder, name)
			item += "			<Filter>%s</Filter>\n" % folder[:-1]
			item += "		</ClCompile>"
			flt_items.append(item)
	flt_filters = "\n".join(flt_filters)
	flt_items = "\n".join(flt_items)

	prj_file = "%s.vcxproj" % prj_name
	prj_guid = "{%s}" % str(uuid.uuid4()).upper()
	prj_text = vs_reference_prj
	prj_text = prj_text.replace("%%%name%%%", prj_name)
	prj_text = prj_text.replace("%%%guid%%%", prj_guid)
	prj_text = prj_text.replace("%%%output%%%", output)
	prj_text = prj_text.replace("%%%defines%%%", defines)
	prj_text = prj_text.replace("%%%includedirs%%%", includedirs)
	prj_text = prj_text.replace("%%%item_groups%%%", items)

	sln_file = "%s.sln" % prj_name
	sln_text = vs_reference_sln
	sln_text = sln_text.replace("%%%name%%%", prj_name)
	sln_text = sln_text.replace("%%%file%%%", prj_file)
	sln_text = sln_text.replace("%%%guid%%%", prj_guid)

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
