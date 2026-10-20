import sys,os
print('MUT')
src=open(sys.argv[0]).read()
dst=f"replica_{os.getpid()}.py"
open(dst,'w').write(src);print(f"REPLICADO: {dst} ({len(src)} chars)")