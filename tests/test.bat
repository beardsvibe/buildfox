@echo off
rem python mask.py --verbose test.mask test_out.mask
rem python mask.py --verbose test.mask test_out.sh
rem python mask.py --verbose test.mask test_out.ninja
rem python ..\mask.py --verbose test.ninja test_out.mask
rem python ..\mask.py --verbose test.ninja test_out.ninja
python ..\mask.py --verbose test.ninja test_out.bat
python ..\mask.py --verbose test_out.bat test_out2.ninja
rem python ..\mask.py --verbose test.ninja test_out.sln
rem python ..\mask.py --verbose test.ninja test_out.pro
rem C:\Qt5.4\5.4\msvc2013_opengl\bin\qmake -tp vc