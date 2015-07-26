[
    {
        "cmd": "cl a.cpp /nologo /showIncludes /Foa.obj t=lool",
        "depend_on": [
            "a.cpp"
        ],
        "touch": [
            "a.obj"
        ]
    },
    {
        "cmd": "cl b.cpp /nologo /showIncludes /Fob.obj t=lool2",
        "depend_on": [
            "b.cpp"
        ],
        "touch": [
            "b.obj"
        ]
    },
    {
        "cmd": "cl a.cpp b.cpp /link /nologo /out:result.exe",
        "depend_on": [
            "a.cpp",
            "b.cpp"
        ],
        "touch": [
            "result.exe"
        ]
    }
]