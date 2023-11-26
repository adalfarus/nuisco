# Nuitka Isolation Compiler (nuisco) Guide
[![Active Development](https://img.shields.io/badge/Maintenance%20Level-Actively%20Developed-brightgreen.svg)](https://gist.github.com/cheerfulstoic/d107229326a01ff0f333a1d3476e068d)
[![Build Status](https://github.com/Adalfarus/nuisco/actions/workflows/python-publish.yml/badge.svg)](https://github.com/Adalfarus/nuisco/actions)
[![License: GPL-3.0](https://img.shields.io/github/license/Adalfarus/nuisco)](https://github.com/Adalfarus/nuisco/blob/main/LICENSE)

The nuisco (Nuitka Isolation Compiler) is designed to enhance the speed of Nuitka compilation while providing greater flexibility in the post-compilation customization. This utility is optimized for Python version 3.11 and should not be utilized with version 3.12.

## Utilizing the Build Feature in Nuisco

When using the build feature in Nuisco, start by placing your project in a directory named after your program (e.g., YOURPROGRAM). Make sure the main script of your project is named main.py. To initiate the build process, use the build sub-command in Nuisco. This command supports additional arguments for including extra libraries. Specify these libraries by their name and type, using the following types:

- Module: For individual scripts or directories containing only Python source files.
- DLL: For any .pyd files.
- Dir: For directories containing files other than Python source files.
- Modulepy: For adding uncompiled Python source files; not to be used for directory packages.
- Dirpy: For copying uncompiled package directories.
- Py: A combination of modulepy and dirpy that automatically selects the appropriate one.

The initial phase involves the compilation of all dependencies of your script, which are then transferred to a directory called compiled_modules. This process might be lengthy, but the benefit lies in the reusability of the compiled modules. However, it is crucial to recompile any modules that were active during a crash, as they may have become corrupted.

Once the dependencies are compiled, the entirety of the program is relocated to a directory named YOURCOMPILEDPROGRAM. If you wish to review the build process for errors, inspect the buildFolder before initiating a new compilation, as it remains intact until then.

For my particular project, the successful command was:

```bash
nuisco build --src=./src --out=./out --extraArgs=select-dll urllib3-module hmac-module email-module http-dirpy
```

Crashes may occur sporadically. Typically, rerunning the script resolves the issue, but if the problem persists, report it on our GitHub repository's bug tracker.

The compiler, like the main script also accepts several types of extra packages, such as [module, dll, dir, modulepy, dirpy and py]. Multi-threading is possible with up to 16 processes, but ensure your system is capable of managing such a load. Adding modules may require manual intervention, utilizing sys.executable, to find your installed python packages.

Special attention is required for the _socket module. Included are two scripts: make_socket and convert_socket. The former generates the socket pyd file, while the latter converts an existing socket to base64 for integration into the make_socket script.

Occasionally, security software may erroneously flag compiled modules as threats, commonly seen with the struct module. If certain it's a false positive, the alert can be deactivated. Otherwise, seek a professional's analysis.

It's imperative to avoid interrupting the build process to prevent incomplete libraries, which may not be recognized as corrupted.

Please note, certain libraries such as https cookiejar or charset normalizer require specific handling. Currently, CookieJar is unsupported.

The multiprocessing feature operates at the script level. Therefore, if one script demands extensive compilation and others do not, the process cannot be expedited. This is to avoid simultaneous compilation of the same library. Enhancements in this area are planned for version clv3.0.

Anticipated updates in clv3.0 include:

- A global registry of package names to enable multiprocessing at a more extensive scale.
- Assessment procedures for compiled libraries to determine if replacements are necessary.
- Verification of the library's operating system, Python version, and architecture prior to duplication.
- A localized checklist of essential imports to minimize the unnecessary bulk of the libs directory.
- Modular level imports to further decrease size, which will be either categorized into directories or modules, necessitating a mechanism to decide the optimal approach.

## Utilizing Built-In Templates with Nuisco
Nuisco comes equipped with pre-defined templates, including the Python Project Template (ppt) and the Python Package Template (ppat). You can create a template at the current location using the sub-command `create-template` followed by the project name and the template name e.g. ppt `--template-name=ppt`. These templates are readily available for use and can be found in the package directory (`%userprofile%/AppData/local/Programs/Python/Python311/Lib/site-packages/nuisco/templates`). Additionally, you have the option to create your own custom templates following the established structure.

To better understand how to configure these templates, let's examine the `ppt-config.json` file:

```json
{
    "files": [
        "src/__init__.py", "src/main.py", 
        "src/modules/classes.py", "src/modules/gui.py", "src/modules/link.py", "src/modules/modulebase.py", 
        "data/Create_your_own.txt", "data/logo-1.ico", "data/logo-1.png", "data/logo-2.ico", "data/logo-2.png", 
        "data/logo-3.ico", "data/logo-3.png", "data/logo-4.ico", "data/logo-4.png", "data/logo-5.ico", 
        "data/logo-5.png", "data/logo-6.ico", "data/logo-6.png", "data/logo-raw.ico", "data/logo-raw.png", 
        "docs/classes.md", "docs/gui.md", "docs/link.md", "docs/main.md", 
        "tests/__init__.py", "tests/test_main.py", 
        "venv/TBA", 
        ".env", ".flake8", "Makefile", "pylint.rc"
    ],
    "os_specific": {
        "Windows": ["build.bat", "create_dist.bat", "install_dist.bat", "install.bat", "run.bat", "inno_setup_script.iss"],
        "Linux": ["build.sh", "create_dist.sh", "install_dist.sh", "install.sh", "run.sh", "scripts.sh"]
    },
    "github_files": [".gitignore", "CONTRIBUTING.md", "README.md", ".git/description", ".github/workflows/ci.yml"],
    "dependencies": {
        "requirements_files": ["dev-requirements.txt"],
        "direct_dependencies": [],
        "force_install_direct_dependencies": false
    },
    "placeholders": {
        "project_name": "{{project_name}}",
        "pyversion": "{{pyversion}}",
        "welcome_message": "{{exec:'Welcome to ' + project_name}}"
    }
}
```

This configuration outlines various options, including advanced settings for different operating systems. A key point to note is that Nuisco will attempt to compile any file located in the `src` directory. Therefore, it is crucial to avoid placing non-source files like text, images, or log files in the `src` directory during compilation, or to remove them beforehand.

### Help Feature in Nuisco
For additional assistance, Nuisco offers a `help` sub-command which provides a list of all sub-commands and the required arguments for them, making it easier to navigate and utilize the platform effectively.
