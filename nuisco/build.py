import subprocess
import os
import shutil
from aplustools.environment import remv
import re
import pkg_resources

def access_resource(relative_path):
    return pkg_resources.resource_filename('nuisco', relative_path)

def build_main(src, out, inLibs, enablePlugins, p, extraArgs):
    def extract_library(line):
        # Handle "import xxx"
        if line.startswith("import "):
            return line.split()[1].split('.')[0]
        # Handle "from xxx import yyy"
        elif line.startswith("from "):
            return line.split()[1].split('.')[0]
        return ""

    def isolate(file):
        with open(os.path.join(__srcdir__, file), "r") as f:
            fileData, f2_lst = [re.sub(r'(?<![\'"])(#.*)', '', line) for line in f.readlines()], [] # re.sub(r'(#.*)', '', line)
        with open(os.path.join(__isocha__, file), "w") as f1:
            f1.write("import config\nimport external_imports\n")
            xy, combined_lines = False, ""
            count = 0
            while count < len(fileData):
                line = fileData[count]
                if line.startswith("import ") or line.startswith("from ") and " import " in line and not "import (" in line: # " import ("
                    lib = extract_library(line)
                    if any([y in lib for y in bundeledLibs]) or any([x in lib for x in internalLibs]): f1.write(line)#; print(f"Writing line to f1: {line}", [y in line for y in bundeledLibs], [x in line for x in internalLibs])
                    else: f2_lst.append(line)#; print(f"Writing line to f2: {line}")
                elif xy or line.startswith("from ") and " import (" in line and line.strip().endswith(','):
                    combined_lines += line.strip()
                    if not line.strip().endswith(','): fileData.append(combined_lines); combined_lines, xy = "", False
                    else: xy = True
                else: f1.write(line)
                count += 1
        with open(os.path.join(__builddir__, "external_imports.py"), "w") as f2:
            for i in f2_lst: f2.write(i)
    
    subprocess.run(["py", "-3.11", "-m", "pip", "install", "nuitka==1.8.4"], check=True)#, "--upgrade"], check=True)

    __builddir__ = ".\\buildFiles"
    __isocha__ = ".\\isolationChamber"
    __srcdir__ = src or ".\\YOURPROGRAM"
    __outdir__ = out or ".\\YOURCOMPILEDPROGRAM"
    internalLibs = inLibs or ["PySide6"] # Libs that need to get tangled into the executable
    enablePlugins = enablePlugins or ["pyside6"]
    bundeledLibs = ["sys", "itertools", "nt", "time", "marshal", "gc", "builtins", "math", "msvcrt", "atexit", "winreg", "array", "errno", "binascii"] # Libs that can't be compiled
    mainFound = False
    processes = p or 2

    extra_args = extraArgs or list()

    for dir in (__builddir__, __isocha__): #, __outdir__
        if not os.path.exists(dir):
            os.mkdir(dir)
        else:
            for i in os.listdir(dir):
                remv(os.path.join(dir, i))
    #for dir in (__srcdir__):
    if not os.path.exists(dir):
        os.mkdir(dir)
    #else: pass
        
    for i in os.listdir(__srcdir__):
        if i != "main.py":
            if os.path.isdir(os.path.join(__srcdir__, i)):
                shutil.copytree(os.path.join(__srcdir__, i), os.path.join(__builddir__, i))
            else:
                shutil.copy(os.path.join(__srcdir__, i), os.path.join(__builddir__, i))
        else: isolate(i); mainFound = True
        
    if not mainFound: shutil.rmtree(__builddir__); os.rmdir(__isocha__); print("Didn't find main.py, please rename your main script, if you haven't already. \nOtherwise, please report this to the bug tracker.")

    print("Preperations done, compiling now!")

    for root, dirs, files in os.walk(__builddir__):
        for file in files:
            print(f"Compiling script {file} ...")
            path = access_resource(".\\compile_libraries_v2.3.py")
            subprocess.run(["py", "-3.11", path, os.path.join(root, file), str(processes)] + extra_args, check=True)
            print("Done compiling, moving on to the next script.")
    # Adjust to your likeing, 2 processes is standard, but every configuration is stable and save (tested up to 8, remember that your cpu is really loaded the more you use (mine was often over 70%, sometimes over 80% and rarely at 100%)

    subprocess.run(["py", "-3.11", "-m", "nuitka", "--standalone", os.path.join(__isocha__, "main.py"), "--nofollow-imports"] + [f"--include-package={c}" for c in internalLibs if c.lower() not in enablePlugins] + #internalLibs + bundeledLibs
                   [f"--enable-plugin={v}" for v in enablePlugins], check=True)

    if os.path.exists(__outdir__): remv(__outdir__)
    shutil.copytree("main.dist", __outdir__)

    #shutil.copy(".\\config.py", __outdir__) # Moved file on second run
    with open(os.path.join(__outdir__, "config.py"), "w") as f:
        f.write("import sys\nsys.path.insert(0, '.\\libs')\n\nimport os\nsys.path[0] = os.path.abspath('.\\libs')")

    if not os.path.exists(os.path.join(__outdir__, "libs")): os.mkdir(os.path.join(__outdir__, "libs"))
    for root, dirs, files in os.walk(".\\compiled_modules"):
        for file in files:
            shutil.copy(os.path.join(root, file), os.path.join(__outdir__, "libs"))
        for dir in dirs:
            shutil.copytree(os.path.join(root, dir), os.path.join(__outdir__, f"libs\\{dir}"))

    shutil.move(os.path.join(__builddir__, "external_imports.py"), __outdir__)

    #subprocess.run(["py", "-3.11", ".\\make_socket.py"], check=True)
    #shutil.move(".\\_socket.pyd", os.path.join(__outdir__, "libs"))

if __name__ == "__main__":
    build_main()
