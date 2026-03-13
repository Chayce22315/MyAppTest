import os, shutil, sys

if len(sys.argv) < 3:
    print("usage: python newapp.py AppName bundle.id")
    sys.exit(1)

name = sys.argv[1]
bundle = sys.argv[2]

src = "template"
dst = name

if os.path.exists(dst):
    print("folder already exists")
    sys.exit(1)

shutil.copytree(src, dst)

# replace placeholders
for root, _, files in os.walk(dst):
    for f in files:
        path = os.path.join(root, f)
        with open(path, "r", encoding="utf-8", errors="ignore") as file:
            data = file.read()
        data = data.replace("MyApp", name)
        data = data.replace("com.example.myapp", bundle)
        with open(path, "w", encoding="utf-8") as file:
            file.write(data)

print("created app:", name)