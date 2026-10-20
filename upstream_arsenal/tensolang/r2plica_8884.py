import sys,os;src=open(sys.argv[0]).read()
dst=f"r2plica_{os.getpid()}.py"
x = len(open(__import__('sys').argv[0]).read())
open(dst,'w').write(src)
print(f"REPLICADO: {dst} ({len(src)} chars)")