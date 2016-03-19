# BuildFox ninja generator

import os
import uuid
import json
from lib_ide_make import gen_make
from lib_util import cxx_findfiles

xcode_reference_prj = r"""
{"archiveVersion": "1",
 "classes": {},
 "objectVersion": "46",
 "objects": {"EF0AF33C1C83A4DC00290920": {"children": [],
                                          "isa": "PBXGroup",
                                          "sourceTree": "<group>"},
             "EF0AF33D1C83A4DC00290920": {"buildConfigurationList": "EF0AF3401C83A4DC00290920",
                                          "compatibilityVersion": "Xcode 3.2",
                                          "hasScannedForEncodings": "0",
                                          "isa": "PBXProject",
                                          "knownRegions": ["en"],
                                          "mainGroup": "EF0AF33C1C83A4DC00290920",
                                          "projectDirPath": "",
                                          "projectRoot": "",
                                          "targets": ["EF0AF3411C83A4DC00290920"]},
             "EF0AF3401C83A4DC00290920": {"buildConfigurations": ["EF0AF3431C83A4DC00290920"],
                                          "defaultConfigurationIsVisible": "0",
                                          "defaultConfigurationName": "Build",
                                          "isa": "XCConfigurationList"},
             "EF0AF3411C83A4DC00290920": {"buildArgumentsString": "$(ACTION)",
                                          "buildConfigurationList": "EF0AF3441C83A4DC00290920",
                                          "buildPhases": [],
                                          "buildToolPath": "/usr/bin/make",
                                          "buildWorkingDirectory": "/Users/jimon/Documents/xcodeproj_tests/test",
                                          "dependencies": [],
                                          "isa": "PBXLegacyTarget",
                                          "name": "test",
                                          "passBuildSettingsInEnvironment": "1",
                                          "productName": "test"},
             "EF0AF3431C83A4DC00290920": {"buildSettings": {},
                                          "isa": "XCBuildConfiguration",
                                          "name": "Build"},
             "EF0AF3441C83A4DC00290920": {"buildConfigurations": ["EF0AF3461C83A4DC00290920"],
                                          "defaultConfigurationIsVisible": "0",
                                          "defaultConfigurationName": "Build",
                                          "isa": "XCConfigurationList"},
             "EF0AF3461C83A4DC00290920": {"buildSettings": {},
                                          "isa": "XCBuildConfiguration",
                                          "name": "Build"}},
 "rootObject": "EF0AF33D1C83A4DC00290920"}
"""

def gen_xcode(all_files, includedirs, prj_name, buildfox_name, cmd_env, ninja_gen_mode):
	gen_make(buildfox_name, cmd_env, ninja_gen_mode)

	all_files = cxx_findfiles(all_files)
	includedirs = [".", "build/bin_debug"] + includedirs

	prj_location = prj_name + ".xcodeproj"
	if not os.path.exists(prj_location):
		os.makedirs(prj_location)

	ref = json.loads(xcode_reference_prj)
	import mod_pbxproj
	prj = mod_pbxproj.XcodeProject(ref, prj_location + "/project.pbxproj")

	target = prj.get_build_phases('PBXLegacyTarget')
	target[0]["buildWorkingDirectory"] = os.path.abspath(prj_location + "/..")

	for file in all_files:
		prj.add_file_if_doesnt_exist(os.path.relpath(file, prj_location + "/.."))

	prj.save()
