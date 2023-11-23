import subprocess
import importlib
import shutil
import sys
import ast
import os
from multiprocessing import Pool
from functools import partial


def execute_python_command(arguments=None, run=False, *args, **kwargs): # Added to remain consistant with executing in same python enviornment
    if arguments == None: arguments = []
    print(' '.join([sys.executable] + arguments))
    if run: arguments.append("--run")
    return subprocess.run([sys.executable] + arguments, *args, **kwargs)

def get_library_path(library): # Taken from get_library_paths, to allow use in other functions
    module = importlib.import_module(library)
    return module.__file__

def get_library_paths(libraries):
    library_paths = {}
    i = 0
    uninstall_switch = False
    while len(library_paths) < len(libraries): # Use while loop, instead of for, to be able to repeat iterations
        library = libraries[i]
        try:
            file_path = get_library_path(library) # If this fails it can't be imported
            library_paths[library] = [file_path, uninstall_switch]
            i += 1
        except ImportError:
            print(f"Failed to import {library}, trying to install it ...") # Trying to install it, if that was the error
            process = execute_python_command(["-m", "pip", "install", library], shell=True, text=True, capture_output=True)
            if process.returncode == 0: # If it succeeded set the uninstall_switch to true, to know to uninstall it later
                uninstall_switch = True
                continue # skip to retry of current iteration, so the uninstall switch doesn't get disabled
            else: i += 1 # If fails continue to next iteration
            library_paths[library] = None
        if uninstall_switch:
            uninstall_switch = False
    return library_paths

def compile_library(library_path, library_name, output_dir, isinit, type="module"):
    os.makedirs(output_dir, exist_ok=True)
    type = type.lower()
    if type == "module": # If it's a module check if the source is a python source file or dir, then act accordingly
        arguments = [
            '-m',
            'nuitka',
            '--module',
            '--follow-import-to=' + library_name,
            '--include-package=' + library_name, # Needs to include itself to prevent circle-import happening
            library_path,
            '--output-dir=' + output_dir,
        ] if isinit else [
            '-m',
            'nuitka',
            '--module',
            '--follow-import-to=' + library_name, # As this doesn't have any file submodules, we can forget about including itself
            library_path,
            '--output-dir=' + output_dir,
        ]
        execute_python_command(arguments, check=True)
    elif type == "dir": # If it's a dir with dlls or other non python-source files, it needs to stay a dir to work properly
        for root, dirs, files in os.walk(library_path):
            for i in files:
                if i.split(".")[-1] == "py" and i.split(".")[-2] != "__init__":
                    execute_python_command([ # If it's python source, compile it
                               '-m', 'nuitka', 
                               '--module', 
                               '--follow-import-to=' + library_name, 
                               os.path.join(root, i), 
                               '--output-dir=' + os.path.join(output_dir, library_name)], run=True)
                    os.remove(os.path.join(output_dir, library_name) + "\\" + i.split(".")[-2] + ".pyi") # Remove .pyi build file
                    shutil.rmtree(os.path.join(output_dir, library_name) + "\\" + i.split(".")[-2] + ".build") # Remove .build build folder
                elif i.split(".")[-1] != "pyc": shutil.copy(os.path.join(root, i), os.path.join(output_dir, library_name)) # else copy it over to the new dir
                else: pass # .pyc files don't need to get copied
    elif type == "dll": # If the target path is a dll, copy it to the output dir
        shutil.copy(library_path, output_dir)
    elif type == "py":
        if os.path.isdir(library_path):
            type = "dirpy"
        elif os.path.isfile(library_path):
            type = "modulepy"
    if type == "modulepy":
        shutil.copy(library_path, output_dir)
    elif type == "dirpy":
        shutil.copytree(library_path, os.path.join(output_dir, library_name))
    else: print("Type", type, "isn't supported.")#; sys.exit(0)
    
def collect_imports(file_path):
    if file_path.split(".")[-1] == "pyd": return list()
    with open(file_path, 'r', encoding='utf-8') as file:
        tree = ast.parse(file.read())
    imports = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for n in node.names:
                imports.add(n.name.split('.')[0])
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imports.add(node.module.split('.')[0])
    return list(imports)
#    imports = []
#    for node in ast.walk(tree):
#        if isinstance(node, ast.Import):
#            for n in node.names:
#                imports.append(n.name)
#                print(n.name)
#        elif isinstance(node, ast.ImportFrom):
#            module_name = node.module
#            if module_name:
#                for n in node.names:
#                    full_name = f"{node.module}.{n.name}" if node.module else n.name
#                    imports.append(full_name)
#                    print(full_name)
#    return imports

def crawl_file(file_path, visited=dict(), depth=0, max_depth=3):
    if not depth < max_depth: return dict()
    else: depth += 1
    imports = collect_imports(file_path)
    tries = file_path.split("\\")[-1].removesuffix(".py")
    module_name_ = tries if tries != "__init__" else file_path.split("\\")[-2]
    if module_name_ not in visited:
        visited[module_name_] = [file_path, False]
    excluded_modules = ["sys", "itertools", "nt", "time", "marshal", "gc", "builtins", "math", "msvcrt", "atexit", "winreg", "array", "errno", "binascii"]
    new_entries = {}
    for module_name in imports:
        if (not module_name in excluded_modules and not module_name in visited):# and not module_name.startswith("_"):
            #print(module_name)
            try:
                import_path = get_library_path(module_name)
                if import_path and import_path not in [v[0] for v in visited.values()]:
                    visited.update(crawl_file(import_path, dict(visited), depth, max_depth))
            except Exception as e: pass#print(e)
    #print(visited)
    return {k: visited[k] for k in visited}#list(visited), list(visited_names)

def crawl_directory(directory):
    all = dict() # Set to avoid repeating lib names
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'): # Check for all python source files in dir
                file_path = os.path.join(root, file)
                a = crawl_file(file_path)
                all.update(a) # Crawl all of them
    return all # Just return all, as it's already in the right format

def compile_and_cleanup(args):
    lib_path, lib_name, output_dir, isinit, type = args
    compile_library(lib_path, lib_name, output_dir, isinit, type)
    
    if type not in ["dir", "dll"]:
        os.remove(os.path.join(output_dir, f"{lib_name}.pyi"))
        shutil.rmtree(os.path.join(output_dir, f"{lib_name}.build"))

def process_library(args, extra_library_types):
    lib_name, data = args
    full_path, uninstall_switch = data
    output_dir = ".\\compiled_modules"
    if "".join(full_path.split("\\")[-1]).split(".")[0] == "__init__":
        isinit = True
    else:
        isinit = False # If library path is a dir set isinit true else false
        
    lib_path = os.path.dirname(full_path) if isinit else full_path # Make path the dir, not the __init__ for nuitka if isinit
    lib_extn = lib_path.split(".")[-1] if not isinit else None # Get the libs extensions for reuse
    
    print("Testing library")
    
    if lib_name in [x.split(".")[0] for x in os.listdir(output_dir)]:
        return # If something without "." is split, it's just a list with one element, so .split(".")[0] should work
    elif lib_name == "compile_libraries_v2.5":
        return # Strange bug, where it compiles itself, but fixed for now
        
    print(lib_path, lib_name, lib_extn)
    
    if lib_name in extra_library_types: # If type was passed, use it
        type = extra_library_types[lib_name]
    elif lib_extn == "pyd": # Determine type
        type = "dll"
    elif lib_extn == "py" or (lib_extn == None and not any(x.endswith((".pyd", ".exe")) for root, dirs, files in os.walk(lib_path) for x in files)):
    #all([x.endswith((".py", ".pyc")) for root, dirs, files in os.walk(lib_path) for x in files])):
        type = "module"
    else:
        type = "dir"
        
    compile_and_cleanup((lib_path, lib_name, output_dir, isinit, type))
        
    if uninstall_switch: execute_python_command(["-m", "pip", "uninstall", lib_name, "-y"], shell=True) # Need to uninstall it after compiling it (if it wasn't installed previously)

def main(path_tc, extra_library_names, extra_library_types, output_dir, processes):
    if path_tc.lower() != "none": # If there is a script to be crawled figure out which type and get lib names
        if os.path.isfile(path_tc): libraries_dict = crawl_file(path_tc)
        elif os.path.isdir(path_tc): libraries_dict = crawl_directory(path_tc)
        else: return
    else: libraries_dict = dict()
    print("Getting lib_paths")
    extra_libraries_dict = get_library_paths(extra_library_names) # Return a dictionary
    #library_paths = {k: [library_paths[i], False] for i, k in enumerate(set(library_names + list(extra_library_paths.keys())))}#dict(k, v for k, v in zip(set(library_paths + list(extra_library_paths.keys())), False))
    libraries_dict.update(extra_libraries_dict)
    print("Crawling deeper ...")
    for i in range(2): # Repeat 2 times to get all nested imports
        print("Repeating")
        more_libraries_dict = dict()
        for r in libraries_dict.values():
            if not r: continue
            i = r[0]#.split(".")[-2] # Need to subsidize r for i
            if os.path.isfile(i):
                more_libraries_dict.update(crawl_file(i))
            elif os.path.isdir(i):
                for root, dirs, files in os.walk(i):
                    for file in files:
                        more_libraries_dict.update(crawl_file(os.path.join(root, file)))
        libraries_dict.update(more_libraries_dict)
        #library_paths = get_library_paths(library_names)
    if path_tc in [u[0] for u in libraries_dict.values()]:
        popped = libraries_dict.pop(next(iter(libraries_dict)))
        print("Removed", popped)
    print("Crawling deeper ...")
    partial_func = partial(process_library, extra_library_types=extra_library_types)
    with Pool(processes=processes) as p: # Adjust to your likeing, 2 is standard, but every configuration is stable and save (tested up to 8, remember that your cpu is really loaded the more you put, mine was often over 70%, sometimes over 80% and rarely at 100%)
        p.map(partial_func, libraries_dict.items())
    sys_path = "\\".join(sys.executable.split("\\")[:-1])
    for i in os.listdir(os.path.join(sys_path, "DLLs\\")):
        if any(x in i for x in ["libcrypto", "libssl", "sqlite3"]) and not os.path.exists(os.path.join(output_dir, i)):
            shutil.copy(os.path.join(sys_path, f"DLLs\\{i}"), output_dir)

if __name__ == '__main__':
    if len(sys.argv) > 1: # If an argument was passed
        path_tc = sys.argv[1]
        processes = int(sys.argv[2])
        extra_library_names, extra_library_types = [], {}
        for i, g in enumerate(sys.argv):
            if i in [0, 1, 2]: continue # Loop over the file name and the passed script name
            g_lst = g.split("-") # Split into module name and type
            extra_library_names.append(g_lst[0])
            extra_library_types[g_lst[0]] = (g_lst[1])
        print("Beginning to crawl ...")
        main(path_tc, extra_library_names, extra_library_types, 'compiled_modules', processes)
    else:
        print("Usage: __main__.py [Python-File] [Extra-Modules]-[type]\nPath to dir or file can be None, Extra-Modules either path or name and type either module, dll or dir.")
