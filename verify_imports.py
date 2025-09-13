#!/usr/bin/env python3
# verify_imports.py — quick check that all modules are available
try:
    import argparse
    import sys
    from collections import deque
    from typing import Deque, Dict
    import pandas as pd
    import numpy as np
except Exception as e:
    print(f"Import failed: {e}")
    raise
else:
    print("All imports OK.")
