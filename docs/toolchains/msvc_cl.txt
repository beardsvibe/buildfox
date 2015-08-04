# CL [option...] file... [option | file]... [lib...] [@command-file] [/link link-opt...]

# Compiler Options Listed by Category
# https://msdn.microsoft.com/en-us/library/19z1t1wy.aspx

# Order of CL Options
# https://msdn.microsoft.com/en-us/library/wf06704c.aspx

# CL Filename Syntax
# https://msdn.microsoft.com/en-us/library/9bk45h3w.aspx

# CL Environment Variables
# https://msdn.microsoft.com/en-us/library/kezkeayy.aspx


#/O1 Creates small code. Equivalent to /Og /Os /Oy /Ob2 /Gs /GF /Gy
#/O2 Creates fast code. Equivalent to /Og /Oi /Ot /Oy /Ob2 /Gs /GF /Gy
#/Ob{0|1|2} Controls inline expansion.
#/Od Disables optimization.
#/Og Uses global optimizations.
#/Oi[-] Generates intrinsic functions.
#/Os Favors small code.
#/Ot Favors fast code.
#/Ox Uses maximum optimization (/Ob2gity /Gs).
#/Oy[-] Omits frame pointer. (x86 only)
#/favor:{blend | ATOM | AMD64 | INTEL64} Produces code that is optimized for a specified architecture, or for a range of architectures.


# TODO

#/arch
#Use SSE or SSE2 instructions in code generation. (x86 only)
#/clr
#Produces an output file to run on the common language runtime.
#/EH
#Specifies the model of exception handling.
#/fp
#Specifies floating-point behavior.
#/GA
#Optimizes for Windows applications.
#/Gd
#Uses the __cdecl calling convention. (x86 only)
#/Ge
#Activates stack probes.
#/GF
#Enables string pooling.
#/Gh
#Calls hook function _penter.
#/GH
#Calls hook function _pexit.
#/GL
#Enables whole program optimization.
#/Gm
#Enables minimal rebuild.
#/GR
#Enables run-time type information (RTTI).
#/Gr
#Uses the __fastcall calling convention. (x86 only)
#/GS
#Checks buffer security.
#/Gs
#Controls stack probes.
#/GT
#Supports fiber safety for data allocated by using static thread-local storage.
#/guard:cf
#Adds control flow guard security checks.
#/Gv
#Uses the __vectorcall calling convention. (x86 and x64 only)
#/Gw
#Enables whole-program global data optimization.
#/GX
#Enables synchronous exception handling.
#/Gy
#Enables function-level linking.
#/GZ
#Enables fast checks. (Same as /RTC1)
#/Gz
#Uses the __stdcall calling convention. (x86 only)
#/homeparams
#Forces parameters passed in registers to be written to their locations on the stack upon function entry. This compiler option is only for the x64 compilers (native and cross compile).
#/hotpatch
#Creates a hotpatchable image.
#/Qfast_transcendentals
#Generates fast transcendentals.
#QIfist
#Suppresses the call of the helper function _ftol when a conversion from a floating-point type to an integral type is required. (x86 only)
#/Qimprecise_fwaits
#Removes fwait commands inside try blocks.
#/Qpar
#Enables automatic parallelization of loops.
#/Qpar-report
#Enables reporting levels for automatic parallelization.
#/Qsafe_fp_loads
#Uses integer move instructions for floating-point values and disables certain floating point load optimizations.
#/Qvec-report (Auto-Vectorizer Reporting Level)
#Enables reporting levels for automatic vectorization.
#/RTC
#Enables run-time error checking.
#/volatile
#Selects how the volatile keyword is interpreted.
#