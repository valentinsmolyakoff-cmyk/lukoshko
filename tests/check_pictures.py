"""Current artwork checks (PNG rendering, Chromium and WebKit)."""
from pathlib import Path
import runpy
runpy.run_path(str(Path(__file__).with_name('check_mobile13.py')),run_name='__main__')
