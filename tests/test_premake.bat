@echo off
cd premake\test
premake5 --scripts=..\premake-ninja ninja
cd build
python ..\..\..\..\mask.py --verbose build.ninja qmake/build.pro
cd ..\..\..

