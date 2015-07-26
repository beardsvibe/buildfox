cl a.cpp /nologo /showIncludes /Foa.obj
cl b.cpp /nologo /showIncludes /Fob.obj
cl a.obj b.obj /link /nologo /out:result.exe
