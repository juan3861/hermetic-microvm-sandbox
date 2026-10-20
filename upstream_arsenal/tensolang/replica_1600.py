import sys,os
src=open(sys.argv[0]).read()
dst=f"replica_{os.getpid()}.py"
# meta-mutation
open(dst,'w').write(src)
print(f"REPLICADO: {dst} ({len(src)} chars)")