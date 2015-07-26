python mask_compiler.py --input test_mask.ir --output test_mask_unsorted.asm
python mask_tool_sort_in_exec_order.py --input test_mask_unsorted.asm --output test_mask_sorted.asm
python mask_gen_shell.py --input test_mask_sorted.asm --output test_mask.bat
python mask_gen_ninja.py --input test_mask_sorted.asm --output test_mask.ninja
