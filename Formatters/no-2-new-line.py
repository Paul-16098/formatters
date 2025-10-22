"""Collapse runs of 3+ newlines down to a single newline.

Behavior is intentionally minimal and matches prior implementation.
"""

from formattersbase import FormattersBase
import re

# Compile once at import time to avoid recompilation on each run.
EXCESS_NEWLINES_RE = re.compile(r"\n{3,}")


with FormattersBase() as f:
    f.file_input = EXCESS_NEWLINES_RE.sub("\n", f.file_input)
