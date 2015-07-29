# cmake

Main reason for adding cmake here is because it used as main project format for some IDE's like clion.

### Grammar

More info [here](http://www.cmake.org/Wiki/CMake/Language_Syntax)

	# This is a comment
	command_name(some_variable another_variable)
	command_name(value) # or with space

	cmake_minimum_required(VERSION 2.8)

	project(test)
	set(variable value)

	# most wonders that command names are case insensitive, like windows file names
	MESSAGE( hi ) # displays "hi"
	message( hi ) # displays "hi" again
	message( HI ) # displays "HI"

	# all this commands print same result "hi"
	MESSAGE(hi)
	MESSAGE (hi)
	MESSAGE( hi )
	MESSAGE (hi )

	# cmake doesn't have expressions, but command can store result in variables
	MATH( EXPR x "3 + 3" ) # stores the result of 3 + 3 in x
	MESSAGE( "x is ${x}" ) # displays "x is 6"
	# using quotes so MESSAGE receives only one argument

	# more stuff
	SET( x a b c   ) # stores "a;b;c" in x
	SET( y "a b c" ) # stores "a b c" in y
	MESSAGE( a b c ) # prints "abc"
	MESSAGE( ${x} )  # prints "abc"
	MESSAGE("${x}")  # prints "a;b;c"
	MESSAGE( ${y} )  # prints "a b c"
	MESSAGE("${y}")  # prints "a b c"

	# meh
	SET( x y A B C )  # stores "y;A;B;C" in x (without quote)
	SET( ${x} )       # => SET( y;A;B;C ) => SET( y A B C)
	SET( y x )        # stores "x" in y (without quotes)
	SET( ${y} y = x ) # => SET( x y )

	# all this command are equal
	SET( x a b c )
	SET( x a;b;c )
	SET( x "a;b;c" )
	SET( x;a;b;c )

	configure_file ( # this will replace all string like @variable_name@ in .in file with actual variable values
		"${PROJECT_SOURCE_DIR}/test.h.in"
		"${PROJECT_BINARY_DIR}/test.h"
	)

	include_directories("${PROJECT_BINARY_DIR}")

	add_library(some_lib some_lib.cpp)

	add_executable(testbin test.cpp)
	target_link_libraries(testbin some_lib)

	install (TARGETS some_lib DESTINATION bin)
	install (FILES some_lib.h DESTINATION include)
	
	#define a macro to simplify adding tests, then use it
	macro (do_test arg result)
		add_test (testbin${arg} testbin ${arg})
		set_tests_properties (testbin${arg}
			PROPERTIES PASS_REGULAR_EXPRESSION ${result})
	endmacro (do_test)

	# do a bunch of result based tests
	do_test (25 "25 is 5")
	do_test (-25 "-25 is 0")

### Commands reference

More info [here](http://www.cmake.org/cmake/help/v3.0/manual/cmake-commands.7.html)

Normal commands

	* add_compile_options
	* add_custom_command
	* add_custom_target
	* add_definitions
	* add_dependencies
	* add_executable
	* add_library
	* add_subdirectory
	* add_test
	* aux_source_directory
	* break
	* build_command
	* cmake_host_system_information
	* cmake_minimum_required
	* cmake_policy
	* configure_file
	* create_test_sourcelist
	* define_property
	* elseif
	* else
	* enable_language
	* enable_testing
	* endforeach
	* endfunction
	* endif
	* endmacro
	* endwhile
	* execute_process
	* export
	* file
	* find_file
	* find_library
	* find_package
	* find_path
	* find_program
	* fltk_wrap_ui
	* foreach
	* function
	* get_cmake_property
	* get_directory_property
	* get_filename_component
	* get_property
	* get_source_file_property
	* get_target_property
	* get_test_property
	* if
	* include_directories
	* include_external_msproject
	* include_regular_expression
	* include
	* install
	* link_directories
	* list
	* load_cache
	* load_command
	* macro
	* mark_as_advanced
	* math
	* message
	* option
	* project
	* qt_wrap_cpp
	* qt_wrap_ui
	* remove_definitions
	* return
	* separate_arguments
	* set_directory_properties
	* set_property
	* set
	* set_source_files_properties
	* set_target_properties
	* set_tests_properties
	* site_name
	* source_group
	* string
	* target_compile_definitions
	* target_compile_options
	* target_include_directories
	* target_link_libraries
	* try_compile
	* try_run
	* unset
	* variable_watch
	* while

Deprecated commands :

	* build_name
	* exec_program
	* export_library_dependencies
	* install_files
	* install_programs
	* install_targets
	* link_libraries
	* make_directory
	* output_required_files
	* remove
	* subdir_depends
	* subdirs
	* use_mangled_mesa
	* utility_source
	* variable_requires
	* write_file

CTest commands :

	* ctest_build
	* ctest_configure
	* ctest_coverage
	* ctest_empty_binary_directory
	* ctest_memcheck
	* ctest_read_custom_files
	* ctest_run_script
	* ctest_sleep
	* ctest_start
	* ctest_submit
	* ctest_test
	* ctest_update
	* ctest_upload

### Varaiables

More info [here](http://www.cmake.org/cmake/help/v3.0/manual/cmake-variables.7.html)

Variables that Provide Information

	* CMAKE_ARGC
	* CMAKE_ARGV0
	* CMAKE_AR
	* CMAKE_BINARY_DIR
	* CMAKE_BUILD_TOOL
	* CMAKE_CACHEFILE_DIR
	* CMAKE_CACHE_MAJOR_VERSION
	* CMAKE_CACHE_MINOR_VERSION
	* CMAKE_CACHE_PATCH_VERSION
	* CMAKE_CFG_INTDIR
	* CMAKE_COMMAND
	* CMAKE_CROSSCOMPILING
	* CMAKE_CTEST_COMMAND
	* CMAKE_CURRENT_BINARY_DIR
	* CMAKE_CURRENT_LIST_DIR
	* CMAKE_CURRENT_LIST_FILE
	* CMAKE_CURRENT_LIST_LINE
	* CMAKE_CURRENT_SOURCE_DIR
	* CMAKE_DL_LIBS
	* CMAKE_EDIT_COMMAND
	* CMAKE_EXECUTABLE_SUFFIX
	* CMAKE_EXTRA_GENERATOR
	* CMAKE_EXTRA_SHARED_LIBRARY_SUFFIXES
	* CMAKE_GENERATOR
	* CMAKE_GENERATOR_TOOLSET
	* CMAKE_HOME_DIRECTORY
	* CMAKE_IMPORT_LIBRARY_PREFIX
	* CMAKE_IMPORT_LIBRARY_SUFFIX
	* CMAKE_JOB_POOL_COMPILE
	* CMAKE_JOB_POOL_LINK
	* CMAKE_LINK_LIBRARY_SUFFIX
	* CMAKE_MAJOR_VERSION
	* CMAKE_MAKE_PROGRAM
	* CMAKE_MINIMUM_REQUIRED_VERSION
	* CMAKE_MINOR_VERSION
	* CMAKE_PARENT_LIST_FILE
	* CMAKE_PATCH_VERSION
	* CMAKE_PROJECT_NAME
	* CMAKE_RANLIB
	* CMAKE_ROOT
	* CMAKE_SCRIPT_MODE_FILE
	* CMAKE_SHARED_LIBRARY_PREFIX
	* CMAKE_SHARED_LIBRARY_SUFFIX
	* CMAKE_SHARED_MODULE_PREFIX
	* CMAKE_SHARED_MODULE_SUFFIX
	* CMAKE_SIZEOF_VOID_P
	* CMAKE_SKIP_INSTALL_RULES
	* CMAKE_SKIP_RPATH
	* CMAKE_SOURCE_DIR
	* CMAKE_STANDARD_LIBRARIES
	* CMAKE_STATIC_LIBRARY_PREFIX
	* CMAKE_STATIC_LIBRARY_SUFFIX
	* CMAKE_TOOLCHAIN_FILE
	* CMAKE_TWEAK_VERSION
	* CMAKE_VERBOSE_MAKEFILE
	* CMAKE_VERSION
	* CMAKE_VS_DEVENV_COMMAND
	* CMAKE_VS_INTEL_Fortran_PROJECT_VERSION
	* CMAKE_VS_MSBUILD_COMMAND
	* CMAKE_VS_MSDEV_COMMAND
	* CMAKE_VS_PLATFORM_TOOLSET
	* CMAKE_XCODE_PLATFORM_TOOLSET
	* PROJECT_BINARY_DIR
	* <PROJECT-NAME>_BINARY_DIR
	* PROJECT_NAME
	* <PROJECT-NAME>_SOURCE_DIR
	* <PROJECT-NAME>_VERSION
	* <PROJECT-NAME>_VERSION_MAJOR
	* <PROJECT-NAME>_VERSION_MINOR
	* <PROJECT-NAME>_VERSION_PATCH
	* <PROJECT-NAME>_VERSION_TWEAK
	* PROJECT_SOURCE_DIR
	* PROJECT_VERSION
	* PROJECT_VERSION_MAJOR
	* PROJECT_VERSION_MINOR
	* PROJECT_VERSION_PATCH
	* PROJECT_VERSION_TWEAK

Variables that Change Behavior

	* BUILD_SHARED_LIBS
	* CMAKE_ABSOLUTE_DESTINATION_FILES
	* CMAKE_APPBUNDLE_PATH
	* CMAKE_AUTOMOC_RELAXED_MODE
	* CMAKE_BACKWARDS_COMPATIBILITY
	* CMAKE_BUILD_TYPE
	* CMAKE_COLOR_MAKEFILE
	* CMAKE_CONFIGURATION_TYPES
	* CMAKE_DEBUG_TARGET_PROPERTIES
	* CMAKE_DISABLE_FIND_PACKAGE_<PackageName>
	* CMAKE_ERROR_DEPRECATED
	* CMAKE_ERROR_ON_ABSOLUTE_INSTALL_DESTINATION
	* CMAKE_SYSROOT
	* CMAKE_FIND_LIBRARY_PREFIXES
	* CMAKE_FIND_LIBRARY_SUFFIXES
	* CMAKE_FIND_NO_INSTALL_PREFIX
	* CMAKE_FIND_PACKAGE_WARN_NO_MODULE
	* CMAKE_FIND_ROOT_PATH
	* CMAKE_FIND_ROOT_PATH_MODE_INCLUDE
	* CMAKE_FIND_ROOT_PATH_MODE_LIBRARY
	* CMAKE_FIND_ROOT_PATH_MODE_PACKAGE
	* CMAKE_FIND_ROOT_PATH_MODE_PROGRAM
	* CMAKE_FRAMEWORK_PATH
	* CMAKE_IGNORE_PATH
	* CMAKE_INCLUDE_PATH
	* CMAKE_INCLUDE_DIRECTORIES_BEFORE
	* CMAKE_INCLUDE_DIRECTORIES_PROJECT_BEFORE
	* CMAKE_INSTALL_DEFAULT_COMPONENT_NAME
	* CMAKE_INSTALL_PREFIX
	* CMAKE_LIBRARY_PATH
	* CMAKE_MFC_FLAG
	* CMAKE_MODULE_PATH
	* CMAKE_NOT_USING_CONFIG_FLAGS
	* CMAKE_POLICY_DEFAULT_CMP<NNNN>
	* CMAKE_POLICY_WARNING_CMP<NNNN>
	* CMAKE_PREFIX_PATH
	* CMAKE_PROGRAM_PATH
	* CMAKE_PROJECT_<PROJECT-NAME>_INCLUDE
	* CMAKE_SKIP_INSTALL_ALL_DEPENDENCY
	* CMAKE_STAGING_PREFIX
	* CMAKE_SYSTEM_IGNORE_PATH
	* CMAKE_SYSTEM_INCLUDE_PATH
	* CMAKE_SYSTEM_LIBRARY_PATH
	* CMAKE_SYSTEM_PREFIX_PATH
	* CMAKE_SYSTEM_PROGRAM_PATH
	* CMAKE_USER_MAKE_RULES_OVERRIDE
	* CMAKE_WARN_DEPRECATED
	* CMAKE_WARN_ON_ABSOLUTE_INSTALL_DESTINATION

Variables that Describe the System

	* APPLE
	* BORLAND
	* CMAKE_CL_64
	* CMAKE_COMPILER_2005
	* CMAKE_HOST_APPLE
	* CMAKE_HOST_SYSTEM_NAME
	* CMAKE_HOST_SYSTEM_PROCESSOR
	* CMAKE_HOST_SYSTEM
	* CMAKE_HOST_SYSTEM_VERSION
	* CMAKE_HOST_UNIX
	* CMAKE_HOST_WIN32
	* CMAKE_LIBRARY_ARCHITECTURE_REGEX
	* CMAKE_LIBRARY_ARCHITECTURE
	* CMAKE_OBJECT_PATH_MAX
	* CMAKE_SYSTEM_NAME
	* CMAKE_SYSTEM_PROCESSOR
	* CMAKE_SYSTEM
	* CMAKE_SYSTEM_VERSION
	* CYGWIN
	* ENV
	* MSVC10
	* MSVC11
	* MSVC12
	* MSVC60
	* MSVC70
	* MSVC71
	* MSVC80
	* MSVC90
	* MSVC_IDE
	* MSVC
	* MSVC_VERSION
	* UNIX
	* WIN32
	* XCODE_VERSION

Variables that Control the Build

	* CMAKE_ARCHIVE_OUTPUT_DIRECTORY
	* CMAKE_AUTOMOC_MOC_OPTIONS
	* CMAKE_AUTOMOC
	* CMAKE_AUTORCC
	* CMAKE_AUTORCC_OPTIONS
	* CMAKE_AUTOUIC
	* CMAKE_AUTOUIC_OPTIONS
	* CMAKE_BUILD_WITH_INSTALL_RPATH
	* CMAKE_<CONFIG>_POSTFIX
	* CMAKE_DEBUG_POSTFIX
	* CMAKE_EXE_LINKER_FLAGS_<CONFIG>
	* CMAKE_EXE_LINKER_FLAGS
	* CMAKE_Fortran_FORMAT
	* CMAKE_Fortran_MODULE_DIRECTORY
	* CMAKE_GNUtoMS
	* CMAKE_INCLUDE_CURRENT_DIR_IN_INTERFACE
	* CMAKE_INCLUDE_CURRENT_DIR
	* CMAKE_INSTALL_NAME_DIR
	* CMAKE_INSTALL_RPATH
	* CMAKE_INSTALL_RPATH_USE_LINK_PATH
	* CMAKE_<LANG>_VISIBILITY_PRESET
	* CMAKE_LIBRARY_OUTPUT_DIRECTORY
	* CMAKE_LIBRARY_PATH_FLAG
	* CMAKE_LINK_DEF_FILE_FLAG
	* CMAKE_LINK_DEPENDS_NO_SHARED
	* CMAKE_LINK_INTERFACE_LIBRARIES
	* CMAKE_LINK_LIBRARY_FILE_FLAG
	* CMAKE_LINK_LIBRARY_FLAG
	* CMAKE_MACOSX_BUNDLE
	* CMAKE_MACOSX_RPATH
	* CMAKE_MAP_IMPORTED_CONFIG_<CONFIG>
	* CMAKE_MODULE_LINKER_FLAGS_<CONFIG>
	* CMAKE_MODULE_LINKER_FLAGS
	* CMAKE_NO_BUILTIN_CHRPATH
	* CMAKE_NO_SYSTEM_FROM_IMPORTED
	* CMAKE_OSX_ARCHITECTURES
	* CMAKE_OSX_DEPLOYMENT_TARGET
	* CMAKE_OSX_SYSROOT
	* CMAKE_PDB_OUTPUT_DIRECTORY
	* CMAKE_PDB_OUTPUT_DIRECTORY_<CONFIG>
	* CMAKE_POSITION_INDEPENDENT_CODE
	* CMAKE_RUNTIME_OUTPUT_DIRECTORY
	* CMAKE_SHARED_LINKER_FLAGS_<CONFIG>
	* CMAKE_SHARED_LINKER_FLAGS
	* CMAKE_SKIP_BUILD_RPATH
	* CMAKE_SKIP_INSTALL_RPATH
	* CMAKE_STATIC_LINKER_FLAGS_<CONFIG>
	* CMAKE_STATIC_LINKER_FLAGS
	* CMAKE_TRY_COMPILE_CONFIGURATION
	* CMAKE_USE_RELATIVE_PATHS
	* CMAKE_VISIBILITY_INLINES_HIDDEN
	* CMAKE_WIN32_EXECUTABLE
	* EXECUTABLE_OUTPUT_PATH
	* LIBRARY_OUTPUT_PATH

Variables for Languages

	* CMAKE_COMPILER_IS_GNU<LANG>
	* CMAKE_Fortran_MODDIR_DEFAULT
	* CMAKE_Fortran_MODDIR_FLAG
	* CMAKE_Fortran_MODOUT_FLAG
	* CMAKE_INTERNAL_PLATFORM_ABI
	* CMAKE_<LANG>_ARCHIVE_APPEND
	* CMAKE_<LANG>_ARCHIVE_CREATE
	* CMAKE_<LANG>_ARCHIVE_FINISH
	* CMAKE_<LANG>_COMPILE_OBJECT
	* CMAKE_<LANG>_COMPILER_ABI
	* CMAKE_<LANG>_COMPILER_ID
	* CMAKE_<LANG>_COMPILER_LOADED
	* CMAKE_<LANG>_COMPILER
	* CMAKE_<LANG>_COMPILER_EXTERNAL_TOOLCHAIN
	* CMAKE_<LANG>_COMPILER_TARGET
	* CMAKE_<LANG>_COMPILER_VERSION
	* CMAKE_<LANG>_CREATE_SHARED_LIBRARY
	* CMAKE_<LANG>_CREATE_SHARED_MODULE
	* CMAKE_<LANG>_CREATE_STATIC_LIBRARY
	* CMAKE_<LANG>_FLAGS_DEBUG
	* CMAKE_<LANG>_FLAGS_MINSIZEREL
	* CMAKE_<LANG>_FLAGS_RELEASE
	* CMAKE_<LANG>_FLAGS_RELWITHDEBINFO
	* CMAKE_<LANG>_FLAGS
	* CMAKE_<LANG>_IGNORE_EXTENSIONS
	* CMAKE_<LANG>_IMPLICIT_INCLUDE_DIRECTORIES
	* CMAKE_<LANG>_IMPLICIT_LINK_DIRECTORIES
	* CMAKE_<LANG>_IMPLICIT_LINK_FRAMEWORK_DIRECTORIES
	* CMAKE_<LANG>_IMPLICIT_LINK_LIBRARIES
	* CMAKE_<LANG>_LIBRARY_ARCHITECTURE
	* CMAKE_<LANG>_LINKER_PREFERENCE_PROPAGATES
	* CMAKE_<LANG>_LINKER_PREFERENCE
	* CMAKE_<LANG>_LINK_EXECUTABLE
	* CMAKE_<LANG>_OUTPUT_EXTENSION
	* CMAKE_<LANG>_PLATFORM_ID
	* CMAKE_<LANG>_SIMULATE_ID
	* CMAKE_<LANG>_SIMULATE_VERSION
	* CMAKE_<LANG>_SIZEOF_DATA_PTR
	* CMAKE_<LANG>_SOURCE_FILE_EXTENSIONS
	* CMAKE_USER_MAKE_RULES_OVERRIDE_<LANG>

Variables for CPack

	* CPACK_ABSOLUTE_DESTINATION_FILES
	* CPACK_COMPONENT_INCLUDE_TOPLEVEL_DIRECTORY
	* CPACK_ERROR_ON_ABSOLUTE_INSTALL_DESTINATION
	* CPACK_INCLUDE_TOPLEVEL_DIRECTORY
	* CPACK_INSTALL_SCRIPT
	* CPACK_PACKAGING_INSTALL_PREFIX
	* CPACK_SET_DESTDIR
	* CPACK_WARN_ON_ABSOLUTE_INSTALL_DESTINATION