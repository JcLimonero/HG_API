"""
Root conftest.py — ensure pyodbc is importable even when libodbc.so.2 is
not installed (e.g. CI / dev machines without an ODBC driver manager).

We attempt a real import first; if it raises ImportError we inject a
MagicMock stand-in so that `database.py` (and tests that patch
`database.pyodbc.connect`) can work without the native shared library.
"""
import sys
from unittest.mock import MagicMock

try:
    import pyodbc  # noqa: F401  — real import succeeds, nothing to do
except ImportError:
    sys.modules["pyodbc"] = MagicMock()
