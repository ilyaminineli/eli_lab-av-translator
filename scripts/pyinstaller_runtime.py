"""Runtime compatibility for a windowed PyInstaller build on Windows.

A GUI-subsystem executable may start with sys.stdout/sys.stderr set to None.
AVTranslator installs a StreamHandler in its file logger, so provide a safe
sink for those streams. Persistent application diagnostics still go to the
per-user log file configured in config.py.
"""

import os
import sys

if sys.stdout is None:
    sys.stdout = open(os.devnull, "w", encoding="utf-8")
if sys.stderr is None:
    sys.stderr = open(os.devnull, "w", encoding="utf-8")
