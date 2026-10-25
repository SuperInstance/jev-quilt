#!/usr/bin/env python3
"""Launcher for the JEV continuous probe.

The real probe script lives at the repository root (``<repo>/jev_continuous_probe.py``)
because it resolves its session directory relative to its own location:
``SESSION_DIR = <script_dir>/research/jev_sessions``.  This copy sits inside
``research/`` so the documented command works verbatim from that directory::

    cd /workspace/research && timeout 60 python3 jev_continuous_probe.py 1

It forwards argv unchanged (positional arg = number of rounds; the root script
defaults to 200, so pass an explicit small count for a single round).
"""
import os
import runpy
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
# research/ -> repo root, following symlinks (/workspace/research is a symlink).
_REAL = os.path.abspath(os.path.join(_HERE, os.pardir, "jev_continuous_probe.py"))
if not os.path.exists(_REAL):
    raise SystemExit(f"FATAL: real probe not found at {_REAL}")
sys.argv[0] = _REAL
runpy.run_path(_REAL, run_name="__main__")
