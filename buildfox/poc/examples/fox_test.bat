python ..\buildfox.py -i fox_test.fox -o fox_test.ninja -d toolset msvc -d variation debug
python ..\buildfox.py -i fox_test.fox -o fox_test_gcc.ninja -d toolset gcc -d variation debug
ninja -f fox_test.ninja
ninja -f fox_test_gcc.ninja