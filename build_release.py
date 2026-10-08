#!/usr/bin/env python3
"""Package the installer, source CSS, documentation and sanitized previews."""
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED

root = Path(__file__).resolve().parent
output = root / 'dist' / 'vesperwing-glass-1.0.0.zip'
output.parent.mkdir(exist_ok=True)
files = [root / n for n in ('README.md', 'LICENSE', 'install.py', 'build_release.py')]
for directory in ('styles', 'screenshots', 'docs'):
    files.extend(p for p in (root / directory).rglob('*') if p.is_file())
with ZipFile(output, 'w', compression=ZIP_DEFLATED) as archive:
    for path in sorted(files):
        archive.write(path, Path('vesperwing-glass-1.0.0') / path.relative_to(root))
print(output)
