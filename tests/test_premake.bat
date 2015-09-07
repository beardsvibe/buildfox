@echo off
cd premake\test
premake5 --scripts=..\premake-ninja ninja
cd build
rem python ..\..\..\..\mask.py --verbose build.ninja qmake/build.pro
python ..\..\..\..\mask.py --verbose build.ninja build.bat
cd ..\..\..

