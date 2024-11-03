# coding: utf-8

# The program analyzer to be optimized
m_tool = "~/SVF/Release+Asserts/bin/wpa -ander".split(' ')

# The LLVM opt for transforming the bitcode
# Currently, we run opt_bin and m_tool independently.
#  1. We first run opt to transform a bitcode
#  2. We then run m_tool on the optimized bitcode
opt_bin = "~/LLVM/llvm3.6/build/Release+Asserts/bin/opt"

# Currently, I only use a subset of the options supported by opt
# Besides, some options might be conflict with each other
opt_options = [
    "dce = false (bool)",  # Dead Code Elimination
    "adce = false (bool)",  # Aggressive DCE
    "argpromotion = false (bool)",  # ArgumentPromotion
    "simplifycfg = false (bool)",  # CFGSimplification
    "deadargelim = false (bool)",  # Dead Argument Elimination
    "die = false (bool)",  # Dead Instruction Elimination
    "dse = false (bool)",  # Dead Store Elimination
    "globaldce = false (bool)",  # Dead Global Elimination
    "inline = false (bool)",  # Function Integration/Inlining
    "gvn = false (bool)",  # Global Value Numbering
    "indvars = false (bool)",  # Induction Variable Simplification
    # "loop-deletion  = false (bool)", # Delete Dead Loops
    "loop-rotate = false (bool)",  # Rotate Loops
    "loop-unroll = false (bool)",  # Unroll loops
    "loop-unswitch = false (bool)",  # Unswitch loops
    "memcpyopt = false (bool)",  # MemCpy Optimization
    "consthoist = false (bool)",  # Constant Hoisting
    "constprop = false (bool)",  # Simple constant propagation
    "flattencfg = false (bool)",  # Flatten the CFG
    "early-cse = false (bool)",  # Early CSE
    "reassociate = false (bool)",  # Reassociate expressions
    "scalarrepl  = false (bool)",  # Scalar Replacement of Aggregates
    "instcombine = false (bool)",  # Combine redundant instructions
    "ipsccp = false (bool)",  # Interprocedural Sparse Conditional Constant Propagation
    "licm = false (bool)",  # Loop Invariant Code Motion
    "loop-instsimplify = false (bool)",  # Simplify instructions in loops
    "loop-reduce = false (bool)",  # Loop Strength Reduction
    "mem2reg = false (bool)",  # Promote Memory to Register
    "sccp = false (bool)"  # Sparse Conditional Constant Propagation
]

