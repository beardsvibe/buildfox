[
    {
        "cmd": "cl /nologo /showIncludes -c test_mask_a.cpp /Fotest_mask_a.obj",
        "depend_on": [
            "test_mask_a.cpp"
        ],
        "touch": [
            "test_mask_a.obj"
        ]
    },
    {
        "cmd": "cl /nologo /showIncludes -c test_mask_b.cpp /Fotest_mask_b.obj",
        "depend_on": [
            "test_mask_b.cpp"
        ],
        "touch": [
            "test_mask_b.obj"
        ]
    },
    {
        "cmd": "cl test_mask_a.obj test_mask_b.obj /link /nologo /out:test_mask_result.exe",
        "depend_on": [
            "test_mask_a.obj",
            "test_mask_b.obj"
        ],
        "touch": [
            "test_mask_result.exe"
        ]
    }
]