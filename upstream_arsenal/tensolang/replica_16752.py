import sys,os
src=open(sys.argv[0]).read()
dst=f"replica_{os.getpid()}.py"
open(dst,'w').write(src)
# meta-mutation
print(f"REPLICADO: {dst} ({len(src)} chars)")