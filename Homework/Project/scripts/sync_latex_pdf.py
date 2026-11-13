"""Copy a successfully built PDF beside its TeX source for consistent previews."""
from pathlib import Path
import shutil
import sys

source = Path(sys.argv[1]).resolve()
build_dir = Path(sys.argv[2]).resolve()
built = build_dir / (source.stem + '.pdf')
destination = source.with_suffix('.pdf')
if not built.is_file():
    raise SystemExit(f'Compiled PDF missing: {built}')
if built != destination:
    shutil.copyfile(built, destination)
print(f'Updated {destination}')
