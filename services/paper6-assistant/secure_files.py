"""Descriptor-relative file access; never follow agent-controlled symlinks."""
import os,secrets,stat
from pathlib import Path
DIR=os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW
class SecureTree:
 def __init__(self,root):self.root=Path(root)
 def parent(self,name,create=False):
  parts=Path(name).parts
  if not parts or Path(name).is_absolute() or any(p in ['..','.'] or p.startswith('.') for p in parts):raise ValueError('Relative visible paths only')
  fd=os.open(self.root,DIR)
  try:
   for part in parts[:-1]:
    if create:
     try:os.mkdir(part,dir_fd=fd)
     except FileExistsError:pass
    nxt=os.open(part,DIR,dir_fd=fd);os.close(fd);fd=nxt
   return fd,parts[-1]
  except:os.close(fd);raise
 def read(self,name,limit=2_000_000):
  fd,leaf=self.parent(name)
  try:
   opened=os.open(leaf,os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK,dir_fd=fd)
   try:
    if not stat.S_ISREG(os.fstat(opened).st_mode):raise ValueError('Regular files only')
    with os.fdopen(opened,'rb',closefd=False) as f:data=f.read(limit+1)
    if len(data)>limit:raise ValueError('Artifact exceeds the read budget')
    return data
   finally:os.close(opened)
  finally:os.close(fd)
 def put(self,name,data):
  if isinstance(data,str):data=data.encode()
  fd,leaf=self.parent(name,True);tmp='tmp-'+secrets.token_hex(10)
  try:
   try:
    info=os.stat(leaf,dir_fd=fd,follow_symlinks=False)
    if not stat.S_ISREG(info.st_mode):raise ValueError('Refusing a nonregular destination')
   except FileNotFoundError:pass
   out=os.open(tmp,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600,dir_fd=fd)
   with os.fdopen(out,'wb') as f:f.write(data)
   os.replace(tmp,leaf,src_dir_fd=fd,dst_dir_fd=fd)
  finally:
   try:os.unlink(tmp,dir_fd=fd)
   except FileNotFoundError:pass
   os.close(fd)
 def names(self):
  result=[]
  for _,dirs,files,fd in os.fwalk(self.root,follow_symlinks=False):
   # fwalk's pinned dir fd protects reads; list results are re-opened safely.
   for leaf in files:
    info=os.stat(leaf,dir_fd=fd,follow_symlinks=False)
    if stat.S_ISREG(info.st_mode):
     path=Path(_)/leaf;relative=str(path.relative_to(self.root))
     if all(not p.startswith('.') for p in Path(relative).parts):result.append(relative)
  return sorted(result)
