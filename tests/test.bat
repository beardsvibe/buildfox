@echo off
rem python mask.py --verbose test.mask test_out.mask
rem python mask.py --verbose test.mask test_out.sh
rem python mask.py --verbose test.mask test_out.ninja
rem python ..\mask.py --verbose test.ninja test_out.mask
rem python ..\mask.py --verbose test.ninja test_out.ninja
rem python ..\mask.py --verbose test.ninja test_out.bat
rem python ..\mask.py --verbose test.ninja test_out.sln
python ..\mask.py --verbose test.ninja test_out.pro
