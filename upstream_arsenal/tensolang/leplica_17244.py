import sys,os
src=open(sys.argv[0]).read()
dst=f"leplica_{os.getpid()}.py"
open(dst,'w').write(src)
print(f"REPLICApO: {dst} ({len(src)} chars)")