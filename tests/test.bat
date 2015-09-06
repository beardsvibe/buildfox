@echo off
rem python ..\mask.py --verbose test.mask test_out.mask
rem python ..\mask.py --verbose test.mask test_out.sh
rem python ..\mask.py --verbose test.mask test_out.ninja
rem python ..\mask.py --verbose test.ninja test_out.mask
rem python ..\mask.py --verbose test.ninja test_out.ninja
rem python ..\mask.py --verbose test.ninja test_out.bat
rem python ..\mask.py --verbose test_out.bat test_out2.ninja
rem python ..\mask.py --verbose test.ninja test_out.sln
rem python ..\mask.py --verbose test2.ninja test_out.pro
rem python ..\mask.py --verbose test.ninja test_out.pro
python ..\mask.py --verbose test_complicated.ninja test/test_out.pro
cd test
rem C:\Qt5.4\5.4\msvc2013_opengl\bin\qmake -tp vc prj_build_ninja_lib.pro
rem C:\Qt5.4\5.4\msvc2013_opengl\bin\qmake -tp vc prj_ninja_exe.pro
C:\Qt5.4\5.4\msvc2013_opengl\bin\qmake -r -tp vc test_out.pro
cd ..