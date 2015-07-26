[
    {
        "cmd": "cl a.cpp /nologo /showIncludes /Foa.obj",
        "depend_on": [
            "a.cpp"
        ],
        "touch": [
            "a.obj"
        ]
    },
    {
        "cmd": "cl b.cpp /nologo /showIncludes /Fob.obj",
        "depend_on": [
            "b.cpp"
        ],
        "touch": [
            "b.obj"
        ]
    },
    {
        "cmd": "cl a.obj b.obj /link /nologo /out:result.exe",
        "depend_on": [
            "a.obj",
            "b.obj"
        ],
        "touch": [
            "result.exe"
        ]
    }
]