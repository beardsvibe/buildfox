@echo off
cd premake\test
premake5 --scripts=..\premake-ninja ninja
cd build
python ..\..\..\..\mask.py --verbose build.ninja build.pro
rem python ..\..\..\..\mask.py --verbose build.ninja build.bat
C:\Qt5.4\5.4\msvc2013_opengl\bin\qmake -r -tp vc build.pro
cd ..\..\..

