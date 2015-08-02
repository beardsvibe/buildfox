python -m grako -o tool_ninja_parser.py -m ninja_ tool_ninja_parser.ebnf
python tool_ninja_parser.py tool_ninja_parser_test2.ninja manifest > tool_ninja_parser_test2.json