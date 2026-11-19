"""Create a manual diagnostic installation ZIP. No invented plugin manifest."""
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
import subprocess,sys
root=Path(__file__).resolve().parents[1]
subprocess.run([sys.executable,str(root/'tools/bundle_runtime.py')],check=True)
output=root/'dist/RN-Deckenbewehrung-0.2.0-diagnose.zip'
output.parent.mkdir(exist_ok=True)
with ZipFile(output,'w',ZIP_DEFLATED) as archive:
    for folder in ('allplan','docs'):
        for path in sorted((root/folder).rglob('*')):
            if path.is_file() and '__pycache__' not in path.parts:
                archive.write(path,path.relative_to(root))
    archive.write(root/'README.md','README.md')
print(output)
