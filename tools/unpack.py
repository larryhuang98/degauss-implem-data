"""Verify and extract the compact datasets. Run from the repository root."""
from pathlib import Path
import json,hashlib,tarfile,tempfile,shutil
root=Path(__file__).resolve().parents[1]; dest=root/'data';dest.mkdir(exist_ok=True)
for group,entry in json.loads((root/'archives.json').read_text()).items():
 with tempfile.TemporaryFile() as joined:
  for part in entry['parts']:
   p=root/part['file'];b=p.read_bytes();assert hashlib.sha256(b).hexdigest()==part['sha256'],p;joined.write(b)
  joined.seek(0)
  with tarfile.open(fileobj=joined,mode='r:xz') as t:
   for m in t.getmembers():
    assert not m.name.startswith('/') and '..' not in Path(m.name).parts
    if m.islnk():assert not m.linkname.startswith('/') and '..' not in Path(m.linkname).parts
   t.extractall(dest,filter='data')
 for f in entry['files']:
  p=dest/f['path'];assert p.stat().st_size==f['bytes'] and hashlib.sha256(p.read_bytes()).hexdigest()==f['sha256'],p
 print(group,'verified',flush=True)
