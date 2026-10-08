#!/usr/bin/env python3
"""Build the experimental add-on from readable sources and shared CSS."""
import json
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED

root = Path(__file__).resolve().parent
version = json.loads((root / 'extension' / 'manifest.json').read_text())['version']
output = root / 'dist' / f'vesperwing-glass-extension-{version}.xpi'
output.parent.mkdir(exist_ok=True)
with ZipFile(output, 'w', compression=ZIP_DEFLATED) as archive:
    for path in sorted((root / 'extension').rglob('*')):
        if path.is_file():
            archive.write(path, path.relative_to(root / 'extension'))
    for path in sorted((root / 'styles').glob('*.css')):
        archive.write(path, path.relative_to(root))
    archive.write(root / 'LICENSE', 'LICENSE')
print(output)
