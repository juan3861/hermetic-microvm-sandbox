import sys,os;src=open(sys.argv[0]).read()
dst=f"replica_{os.getpid()}.py"
x = len(open(__import__('sys').argv[0]).read())
open(dst,'w').write(src)
x = len(open(__import__('sys').argv[0]).read())
print(f"REPLICADO: {dst} ({len(src)} chars)")