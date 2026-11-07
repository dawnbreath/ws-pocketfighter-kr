"""Repository-relative paths (override the root with PF_ROOT). Game data (orig/pf.ws), fonts and generated JSON are git-ignored."""
import os
from pathlib import Path
ROOT = os.environ.get('PF_ROOT') or str(Path(__file__).resolve().parents[1])
TMP = os.environ.get('PF_TMP') or os.path.join(ROOT, 'work', 'tmp')
