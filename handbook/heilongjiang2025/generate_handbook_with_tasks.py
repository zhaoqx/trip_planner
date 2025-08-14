"""
Generate the Teen Handbook PDF with task/checklist sections included.
This is a thin wrapper over generate_handbook_strict that flips the
INCLUDE_TASKS switch and writes to a distinct output filename.

Output: 《2025黑龙江旅行手册_含任务版》.pdf
"""
from __future__ import annotations

import generate_handbook_strict as base

# Ensure tasks are included in notes
base.INCLUDE_TASKS = True

# Write to a distinct output file name
base.OUTPUT = base.BASE_DIR / '《2025黑龙江旅行手册_含任务版》.pdf'

if __name__ == '__main__':
    base.register_font()
    base.main()
