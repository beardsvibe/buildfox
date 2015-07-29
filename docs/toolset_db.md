# Toolset database

To generate mask IR you need extensive knowledge about your target toolset. You can implement this on your own, or you can use provided json configurations.

For example msvc.json :

	{
		"commands":
		{
			"c->obj": "cl $cflags -c $in $out"
			"cpp->obj": "cl $cflags -c $in $out"
			"obj->exe": "cl $lflags /link -o $out $in"
			...
		},
		"flags":
		{
			"cflags":
			{
				"debug": "..."
				"fast": "..."
				"size": "..."
				...
			},
			"lflags":
			{
				...
			}
		},
		"ext_object": ".obj"
		"ext_lib_static": ".lib"
		"ext_lib_dynamic": ".dll"
		...
	}

