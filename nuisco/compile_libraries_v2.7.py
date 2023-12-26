import sys
from enum import Enum
import os
import pkg_resources
import importlib
import subprocess
import ast
from subprocess import CompletedProcess
from multiprocessing import Pool
import shutil

class LogType(Enum):
    INFO = "[INFO] "
    WARN = "[WARN] "
    ERR = "[ERR] "
    DEBUG = "[DEB] "

# Load from settings in clv3.0
excluded_modules = ["sys", "itertools", "nt", "time", "marshal", "gc", "builtins", "math", "msvcrt", "atexit", "winreg", "array", "errno", "binascii"]
access_resource_root_path = pkg_resources.resource_filename('nuisco', './')
allowed_log_types = [LogType.INFO, LogType.WARN, LogType.ERR, LogType.DEBUG]

def access_resource(relative_path: str) -> str:
    return os.path.join(access_resource_root_path, relative_path)

def log(message: str, type: LogType) -> None:
    if type in allowed_log_types:
        print(type + message)

def collect_imports(file_path: str) -> list:
    if file_path.endswith(".pyd"):
        return []
    with open(file_path, "r", encoding="utf-8") as file:
        tree = ast.parse(file.read())
    imports = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for n in node.names:
                imports.add(n.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imports.add(node.module.split(".")[0])
    return list(imports)

def execute_python_command(arguments: list=None, run: bool=False, *args, **kwargs) -> CompletedProcess[str]:
    if arguments == None: arguments = []
    log(' '.join([sys.executable] + arguments), LogType.DEBUG)
    if run: arguments.append("--run") # Added to remain consistent with executing in same python environment
    return subprocess.run([sys.executable] + arguments, *args, **kwargs)

def get_library(library_name: str, iteration: int=0) -> tuple:
    try:
        module = importlib.import_module(library_name)
        return (module.__file__, False if iteration == 0 else True)
    except ImportError:
        if iteration != 0:
            log(f'Failed to install "{library_name}", continuing with next library ...')
            return (None, None)
        log(f'Failed to import "{library_name}", trying to install it ...', LogType.INFO)
        process = execute_python_command(["-m", "pip", "install", library_name], shell=True, text=True, capture_output=True)
        if process.returncode == 0: # If it succeeded set the uninstall_switch to true, to know to uninstall it later
            return get_library(library_name, 1)
        else:
            return (None, None)

def crawl_file(file_path: str, visited: dict={}, depth: int=0, max_depth: int=3, uninstall_current_library: bool=False) -> dict:
    if depth >= max_depth:
        return dict()
    depth += 1
    
    imports = collect_imports(file_path)
    
    file_name = file_path.split("\\")[-1].removesuffix(".py")
    if file_name != "__init__":
        main_module_name = file_name
    else:
        main_module_name = file_path.split("\\")[-2] 
    
    if main_module_name not in visited:
        visited[main_module_name] = [file_path, "", uninstall_current_library]
    
    for module_name in imports:
        if not module_name in excluded_modules and not module_name in visited:
            log("Found" + module_name, LogType.DEBUG)
            try:
                import_path, uninstall_library = get_library(module_name)
                if import_path and import_path not in [x[0] for x in visited.values()]:
                    visited.update(crawl_file(import_path, visited, depth, max_depth, uninstall_library))
            except Exception as e:
                log("An error occurred" + e, LogType.DEBUG)
    return visited

def crawl_dir(dir: str, visited: dict={}) -> dict:
    libraries = visited or {}
    for root, dirs, files in os.walk(dir):
        for file in files: # Only check python source files
            if file.endswith(".py"):
                file_path = os.path.join(root, file)
                file_libraries = crawl_file(file_path, visited=libraries)
                libraries.update(file_libraries) # Add file_libraries to all libraries
    return libraries

def get_libraries(library_names: str) -> dict:
    libraries = {}
    for library_name in library_names:
        if not library_name in libraries:
            libraries[library_name] = get_library(library_name)
    return libraries

def process_library(args):
    library_name, (library_path, library_type, uninstall_library) = args
    output_dir = access_resource(".\\compiled_modules")
    # If library path is a dir set isInit True else False
    isInit = library_path.split("\\")[-1].split(".")[0] == "__init__"
    
    # Make path the dir, not the __init__ for nuitka if isInit
    prepared_library_path = os.path.dirname(library_path) if isInit else library_path
    # Get the libs extensions for reuse if isInit
    library_extension = prepared_library_path.split(".")[-1] if not isInit else None
    
    log(f"Testing library {library_name} ...", LogType.INFO)
    
    if library_name in [x.split(".")[0] for x in os.listdir(output_dir)]: # Check for processor, python version and name
        return # If something without "." is split, it's just a list with one element, so .split(".")[0] should work
    elif library_name == "compile_libraries_v2.7": # Hopefully this doesn't happen anymore
        return # Strange bug, where it compiles itself, but fixed for now
    
    log(f"{library_name} {prepared_library_path} {library_extension}", LogType.DEBUG)
    
    if library_type != "":
        library_type = library_type
    elif library_extension == "pyd": # Determine the type if it wasn't passed
        library_type = "dll"
    elif library_extension == "py" or (library_extension == None and not any(x.endswith(".pyd", ".exe")) 
                                       for root, dirs, files in os.walk(prepared_library_path) 
                                       for x in files):
        library_type = "module"
    else:
        library_type = "dir"
        
    compile_and_cleanup((library_name, prepared_library_path, library_type, isInit, output_dir))
    
    if uninstall_library:
        # Need to uninstall it after compiling it (if it wasn't installed previously)
        execute_python_command(["-m", "pip", "uninstall", library_name, "-y"], shell=True)

def compile_and_cleanup(args):
    library_name, prepared_library_path, library_type, isInit, output_dir = args
    compile_library(library_name, prepared_library_path, library_type, isInit, output_dir)
    
    if library_type not in ["dir", "dll"]:
        os.remove(os.path.join(output_dir, f"{library_name}.pyi"))
        shutil.rmtree(os.path.join(output_dir, f"{library_name}.build"))
        
def compile_library(library_name, library_path, library_type, isInit, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    library_type = library_type.upper()
     # If it's a module check if the source is a python source file or dir, then act accordingly
    if library_type == "MODULE":
        arguments = [
            '-m',
            'nuitka',
            '--module',
            '--follow-import-to=' + library_name,
            '--include-package=' + library_name, # Needs to include itself to prevent circle-import happening
            library_path,
            '--output-dir=' + output_dir,
        ] if isInit else [
            '-m',
            'nuitka',
            '--module',
            '--follow-import-to=' + library_name, # As this doesn't have any file submodules, we can forget about including itself
            library_path,
            '--output-dir=' + output_dir,
        ]
        execute_python_command(arguments, check=True)
    # If it's a dir with dlls or other non python-source files, it needs to stay a dir to work properly
    elif library_type == "DIR":
        for root, dirs, files in os.walk(library_path):
            for file in files:
                if file.endswith(".py") and not file.split(".")[-2] == "__init__":
                    # If it's python source, compile it
                    execute_python_command([
                        '-m', 'nuitka', 
                        '--module', 
                        '--follow-import-to=' + library_name, 
                        os.path.join(root, file), 
                        '--output-dir=' + os.path.join(output_dir, library_name)
                    ], run=True)
                    # Remove .pyi build file
                    os.remove(os.path.join(output_dir, library_name) + "\\" + file.split(".")[-2] + ".pyi")
                    # Remove .build build folder
                    shutil.rmtree(os.path.join(output_dir, library_name) + "\\" + file.split(".")[-2] + ".build")
                # else copy it over to the new dir
                elif not file.endswith(".pyc"):
                    shutil.copy(os.path.join(root, file), os.path.join(output_dir, library_name))
                # .pyc files don't need to get copied
                else:
                    pass
    # If the target path is a dll, copy it to the output dir
    elif library_type == "DLL":
        shutil.copy(library_path, output_dir)
    elif library_type == "PY":
        if os.path.isdir(library_path):
            library_type = "DIRPY"
        elif os.path.isfile(library_path):
            library_type = "MODULEPY"
    
    # If the files remain in python source, just copy them to the output dir
    if library_type == "MODULEPY":
        shutil.copy(library_path, output_dir)
    elif library_type == "DIRPY":
        shutil.copytree(library_path, os.path.join(output_dir, library_name))
    else:
        log(f'Type "{library_type}" is not supported.', LogType.INFO)

def main(path_tc: str, thread_number: int=1, extra_libraries: dict={}, output_dir: str="./output"):
    if path_tc.upper() != "NONE":
        if os.path.isfile(path_tc):
            libraries = crawl_file(path_tc, visited=extra_libraries)
        elif os.path.isdir(path_tc):
            libraries = crawl_dir(path_tc, visited=extra_libraries)
        else:
            libraries = {}
            
        log("Getting library paths ...", LogType.INFO)
        for library_name, values in get_libraries(extra_libraries).items():
            extra_libraries[library_name] = [values[0], extra_libraries[library_name][1], values[2]]
        libraries.update(extra_libraries)
        
        log("Crawling deeper ...", LogType.INFO)
        for i in range(2):
            if i > 0:
                log("Repeating ...", LogType.INFO)
            more_libraries = {}
            for path, type, uninstall in libraries.values():
                if os.path.isfile(path):
                    more_libraries.update(crawl_file(path, visited=libraries, uninstall_current_library=uninstall))
                elif os.path.isdir(path):
                    more_libraries.update(crawl_dir(path, visited=libraries))
            libraries.update(more_libraries)
        
        if path_tc in [x[0] for x in libraries.values()]:
            log(f"Removed {libraries.pop(next(iter(libraries)))}.", LogType.INFO)
        
        log("Compiling found libraries ...", LogType.INFO)
        with Pool(processes=thread_number) as p: # Adjust to your liking, 2 is standard, but every configuration is stable and save (tested up to 8, remember that your cpu is really loaded the more you put, mine was often over 70%, sometimes over 80% and rarely at 100%)
            p.map(process_library, libraries.items())
        
        log("Getting required DLLs ...", LogType.INFO)
        sys_path = "\\".join(sys.executable.split("\\")[:-1])
        for i in os.listdir(os.path.join(sys_path, "DLLS\\")):
            if any(x in i for x in ["libcrypto", "libssl", "sqlite3"]) and not os.path.exists(os.path.join(output_dir, i)):
                shutil.copy(os.path.join(sys_path, f"DLLs\\{i}"), output_dir)
            
# The libraries are stored like this: {"library_name": ["library_path", "library_type", "uninstall_library"]}
if __name__ == "__main__":
    if len(sys.argv) > 1:
        path_to_compile = sys.argv[1]
        thread_number = int(sys.argv[2])
        extra_libraries = {}
        for i, arg in enumerate(sys.argv):
            if i in [0, 1, 2]: continue # Skip ptc, tn and el
            extra_library_name, extra_library_type = arg.split("-") # Split argument into module name and type
            if not extra_library_type.upper() in ["MODULE", "DLL", "DIR", "MODULEPY", "DIRPY", "PY"]:
                log(f'Unknown library type "{extra_library_type.upper()}"', LogType.WARN)
                continue
            extra_libraries[extra_library_name] = ["", extra_library_type.upper(), False]
        log("Read all args, beginning to crawl now ...", LogType.INFO)
        compiled_modules_path = access_resource("compiled_modules")
        if not os.path.exists(compiled_modules_path):
            os.mkdir(compiled_modules_path)
        main(path_to_compile, thread_number, extra_libraries, compiled_modules_path)
    else:
        log("Usage: build.py [Python-File] [Thread-Number] [Extra-Module]-[type]*n\nPath to dir or file can be None, Extra-Modules either path or name and type either module, dll or dir.")
        #'compiled_modules'
