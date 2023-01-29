Basic typechecker enforcer using mypy
=====================================

Add `include pypycheck as _check; _check.check(__file__)` to the top of python
files to automatically run type checking when ever the file changes on first
run.
