# qmake

Looks like qmake posses a lot of information about toolsets and Qt internals.

### Grammar

	# this is comment
	VAR =  value
	VAR += value
	VAR -= value
	VAR *= value # adds value to VAR only if value is not already there
	VAR ~= s/QT_[DT].+/QT # replace everything, that matches QT_D or QT_T, with QT
	VAR = $$OTHER_VAR $$YET_ANOTHER_VAR # immediate var expansion, but you need space if you want to add another var after first one
	VAR = $${OTHER_VAR}$${YET_ANOTHER_VAR} # immediate var expansion and you dont need space between vars
	VAR = $OTHER_VAR # this will be expanded when underlying Makefile is executed
	VAR = $$[QT_VERSION] # access to some internal qmake variables

	message(hello world $$VAR)

	target.path = value # TODO

	win32 { # win32 is <condition>, not that { can only be on this line
		VAR = some_value 
	}
	!win32 { # or this
		...
	}
	macx {
		CONFIG(debug, debug|release) { # this thing is true if CONFIG only contains debug but not release
			HEADERS += debugging.h # for some reason CONFIG can be debug and release on a same time (wtf srsly?)
		}
	}
	macx:CONFIG(debug, debug|release) { # or like this
		HEADERS += debugging.h
	}
	win32:DEFINES += USE_MY_STUFF # or even simpler
	win32:xml { # if win32 + xml
		message(Building for Windows)
		SOURCES += xmlhandler_win.cpp
	} else:xml { # if xml
		SOURCES += xmlhandler.cpp
	} else { # else
		message("Unknown configuration")
	}

	# configs are a bit crazy, everything is CONFIG is available as namescope element
	CONFIG += opengl
	opengl {
		TARGET = application-gl
	} else {
		TARGET = application
	}

	# qmake also have some functions that called "replaced functions"
	HEADERS = $$unique(HEADERS)
	# and you can define your own
	defineReplace(headersAndSources) {
		variable = $$1
		names = $$eval($$variable)
		headers =
		sources =

		for(name, names) {
			header = $${name}.h
			exists($$header) {
				headers += $$header
			}
			source = $${name}.cpp
			exists($$source) {
				sources += $$source
			}
		}
		return($$headers $$sources)
	}
	# qmake also have some other functions called "test functions"

### Variables

Full list [here](http://doc.qt.io/qt-5/qmake-variable-reference.html)

	* CONFIG
	* DEFINES
	* DEF_FILE
	* DEPENDPATH
	* DEPLOYMENT
	* DEPLOYMENT_PLUGIN
	* DESTDIR
	* DISTFILES
	* DLLDESTDIR
	* FORMS
	* GUID
	* HEADERS
	* ICON
	* IDLSOURCES
	* INCLUDEPATH
	* INSTALLS
	* LEXIMPLS
	* LEXOBJECTS
	* LEXSOURCES
	* LIBS
	* LITERAL_HASH
	* MAKEFILE
	* MAKEFILE_GENERATOR
	* MSVCPROJ_*
	* MOC_DIR
	* OBJECTS
	* OBJECTS_DIR
	* POST_TARGETDEPS
	* PRE_TARGETDEPS
	* PRECOMPILED_HEADER
	* PWD
	* OUT_PWD
	* QMAKE
	* QMAKESPEC
	* QMAKE_AR_CMD
	* QMAKE_BUNDLE_DATA
	* QMAKE_BUNDLE_EXTENSION
	* QMAKE_CC
	* QMAKE_CFLAGS
	* QMAKE_CFLAGS_DEBUG
	* QMAKE_CFLAGS_RELEASE
	* QMAKE_CFLAGS_SHLIB
	* QMAKE_CFLAGS_THREAD
	* QMAKE_CFLAGS_WARN_OFF
	* QMAKE_CFLAGS_WARN_ON
	* QMAKE_CLEAN
	* QMAKE_CXX
	* QMAKE_CXXFLAGS
	* QMAKE_CXXFLAGS_DEBUG
	* QMAKE_CXXFLAGS_RELEASE
	* QMAKE_CXXFLAGS_SHLIB
	* QMAKE_CXXFLAGS_THREAD
	* QMAKE_CXXFLAGS_WARN_OFF
	* QMAKE_CXXFLAGS_WARN_ON
	* QMAKE_DISTCLEAN
	* QMAKE_EXTENSION_SHLIB
	* QMAKE_EXT_MOC
	* QMAKE_EXT_UI
	* QMAKE_EXT_PRL
	* QMAKE_EXT_LEX
	* QMAKE_EXT_YACC
	* QMAKE_EXT_OBJ
	* QMAKE_EXT_CPP
	* QMAKE_EXT_H
	* QMAKE_EXTRA_COMPILERS
	* QMAKE_EXTRA_TARGETS
	* QMAKE_FAILED_REQUIREMENTS
	* QMAKE_FRAMEWORK_BUNDLE_NAME
	* QMAKE_FRAMEWORK_VERSION
	* QMAKE_INCDIR
	* QMAKE_INCDIR_EGL
	* QMAKE_INCDIR_OPENGL
	* QMAKE_INCDIR_OPENGL_ES2
	* QMAKE_INCDIR_OPENVG
	* QMAKE_INCDIR_X11
	* QMAKE_INFO_PLIST
	* QMAKE_LFLAGS
	* QMAKE_LFLAGS_CONSOLE
	* QMAKE_LFLAGS_DEBUG
	* QMAKE_LFLAGS_PLUGIN
	* QMAKE_LFLAGS_RPATH
	* QMAKE_LFLAGS_RPATHLINK
	* QMAKE_LFLAGS_RELEASE
	* QMAKE_LFLAGS_APP
	* QMAKE_LFLAGS_SHLIB
	* QMAKE_LFLAGS_SONAME
	* QMAKE_LFLAGS_THREAD
	* QMAKE_LFLAGS_WINDOWS
	* QMAKE_LIBDIR
	* QMAKE_LIBDIR_FLAGS
	* QMAKE_LIBDIR_EGL
	* QMAKE_LIBDIR_OPENGL
	* QMAKE_LIBDIR_OPENVG
	* QMAKE_LIBDIR_X11
	* QMAKE_LIBS
	* QMAKE_LIBS_EGL
	* QMAKE_LIBS_OPENGL
	* QMAKE_LIBS_OPENGL_ES1, QMAKE_LIBS_OPENGL_ES2
	* QMAKE_LIBS_OPENVG
	* QMAKE_LIBS_THREAD
	* QMAKE_LIBS_X11
	* QMAKE_LIB_FLAG
	* QMAKE_LINK_SHLIB_CMD
	* QMAKE_LN_SHLIB
	* QMAKE_POST_LINK
	* QMAKE_PRE_LINK
	* QMAKE_PROJECT_NAME
	* QMAKE_MAC_SDK
	* QMAKE_MACOSX_DEPLOYMENT_TARGET
	* QMAKE_MAKEFILE
	* QMAKE_QMAKE
	* QMAKE_RESOURCE_FLAGS
	* QMAKE_RPATHDIR
	* QMAKE_RPATHLINKDIR
	* QMAKE_RUN_CC
	* QMAKE_RUN_CC_IMP
	* QMAKE_RUN_CXX
	* QMAKE_RUN_CXX_IMP
	* QMAKE_SONAME_PREFIX
	* QMAKE_TARGET
	* QMAKE_TARGET_COMPANY
	* QMAKE_TARGET_DESCRIPTION
	* QMAKE_TARGET_COPYRIGHT
	* QMAKE_TARGET_PRODUCT
	* QT
	* QTPLUGIN
	* QT_VERSION
	* QT_MAJOR_VERSION
	* QT_MINOR_VERSION
	* QT_PATCH_VERSION
	* RC_FILE
	* RC_CODEPAGE
	* RC_ICONS
	* RC_LANG
	* RC_INCLUDEPATH
	* RCC_DIR
	* REQUIRES
	* RESOURCES
	* RES_FILE
	* SIGNATURE_FILE
	* SOURCES
	* SUBDIRS
	* TARGET
	* TARGET_EXT
	* TARGET_x
	* TARGET_x.y.z
	* TEMPLATE
	* TRANSLATIONS
	* UI_DIR
	* VERSION
	* VERSION_PE_HEADER
	* VER_MAJ
	* VER_MIN
	* VER_PAT
	* VPATH
	* WINRT_MANIFEST
	* YACCSOURCES
	* _PRO_FILE_
	* _PRO_FILE_PWD_

### Internal Variables

TODO not sure if this is a full list

	* QT_VERSION
	* QT_INSTALL_PREFIX
	* QT_INSTALL_DOCS
	* QT_INSTALL_HEADERS
	* QT_INSTALL_LIBS
	* QT_INSTALL_BINS
	* QT_INSTALL_PLUGINS
	* QT_INSTALL_DATA
	* QT_INSTALL_TRANSLATIONS
	* QT_INSTALL_CONFIGURATION
	* QT_INSTALL_EXAMPLES

### Replace functions

Full list [here](http://doc.qt.io/qt-5/qmake-function-reference.html)

	* absolute_path(path[, base])
	* basename(variablename)
	* cat(filename[, mode])
	* clean_path(path)
	* dirname(file)
	* enumerate_vars
	* escape_expand(arg1 [, arg2 ..., argn])
	* find(variablename, substr)
	* first(variablename)
	* format_number(number[, options...])
	* fromfile(filename, variablename)
	* getenv(variablename)
	* join(variablename, glue, before, after)
	* last(variablename)
	* list(arg1 [, arg2 ..., argn])
	* lower(arg1 [, arg2 ..., argn])
	* member(variablename, position)
	* prompt(question)
	* quote(string)
	* re_escape(string)
	* relative_path(filePath[, base])
	* replace(string, old_string, new_string)
	* sprintf(string, arguments...)
	* resolve_depends(variablename, prefix)
	* reverse(variablename)
	* section(variablename, separator, begin, end)
	* shadowed(path)
	* shell_path(path)
	* shell_quote(arg)
	* size(variablename)
	* sort_depends(variablename, prefix)
	* split(variablename, separator)
	* system(command[, mode])
	* system_path(path)
	* system_quote(arg)
	* unique(variablename)
	* upper(arg1 [, arg2 ..., argn])
	* val_escape(variablename)

### Test functions

Full list [here](http://doc.qt.io/qt-5/qmake-test-function-reference.html)

	* cache(variablename, [set|add|sub] [transient] [super|stash], [source variablename])
	* CONFIG(config)
	* contains(variablename, value)
	* count(variablename, number)
	* debug(level, message)
	* defined(name[, type])
	* equals(variablename, value)
	* error(string)
	* eval(string)
	* exists(filename)
	* export(variablename)
	* files(pattern[, recursive=false])
	* for(iterate, list)
	* greaterThan(variablename, value)
	* if(condition)
	* include(filename)
	* infile(filename, var, val)
	* isActiveConfig
	* isEmpty(variablename)
	* isEqual
	* lessThan(variablename, value)
	* load(feature)
	* log(message)
	* message(string)
	* mkpath(dirPath)
	* requires(condition)
	* system(command)
	* touch(filename, reference_filename)
	* unset(variablename)
	* warning(string)
	* write_file(filename, [variablename, [mode]])
	* packagesExist(packages)
	* prepareRecursiveTarget(target)
	* qtCompileTest(test)
	* qtHaveModule(name)
