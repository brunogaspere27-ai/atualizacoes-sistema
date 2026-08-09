#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Launcher script for CW Transportadora
Bypasses encoding issues
"""

import sys
import os

# Set UTF-8 encoding
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

print("[LAUNCHER] Starting CW Transportadora...", flush=True)

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import and run
try:
    import main_pyside6
    print("[LAUNCHER] main_pyside6 imported", flush=True)
    main_pyside6.main()
except SystemExit as e:
    print(f"[LAUNCHER] SystemExit: {e.code}", flush=True)
    sys.exit(e.code)
except Exception as e:
    print(f"[LAUNCHER] Error: {e}", flush=True)
    import traceback
    traceback.print_exc()
    sys.exit(1)
