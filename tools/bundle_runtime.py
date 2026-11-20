"""Bundle stdlib-only inspection modules; fail if stale files are shipped."""
from pathlib import Path
import shutil
root=Path(__file__).resolve().parents[1]
target=root/'allplan/PythonPartsScripts/rn_deckenbewehrung'
target.mkdir(exist_ok=True)
for name in ('__init__.py','model.py','asf.py','solid.py'):
    shutil.copyfile(root/'src/rn_deckenbewehrung'/name,target/name)
