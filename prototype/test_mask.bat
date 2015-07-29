cl /nologo /showIncludes -c test_mask_a.cpp /Fotest_mask_a.obj
cl /nologo /showIncludes -c test_mask_b.cpp /Fotest_mask_b.obj
cl test_mask_a.obj test_mask_b.obj /link /nologo /out:test_mask_result.exe
