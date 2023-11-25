# Nuitka Isolation Compiler (nuisco) Guide
[![Active Development](https://img.shields.io/badge/Maintenance%20Level-Actively%20Developed-brightgreen.svg)](https://gist.github.com/cheerfulstoic/d107229326a01ff0f333a1d3476e068d)
[![Build Status](https://github.com/Adalfarus/nic/actions/workflows/python-publish.yml/badge.svg)](https://github.com/Adalfarus/nic/actions)
[![License: GPL-3.0](https://img.shields.io/github/license/Adalfarus/nic)](https://github.com/Adalfarus/nic/blob/main/LICENSE)

The nuisco (Nuitka Isolation Compiler) is designed to enhance the speed of Nuitka compilation while providing greater flexibility in the post-compilation customization. This utility is optimized for Python version 3.11 and should not be utilized with version 3.12.

To begin, place your project within a directory named YOURPROGRAM. Ensure that the primary script, which initiates your program, is labeled as main.py. When this is set up, execute the build.py script. Additional arguments can be provided to include extra libraries, which should be specified with the library name followed by its type from the following list: [module, dll, dir, modulepy, dirpy, py].

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
py -3.11 build.py select-dll urllib3-module hmac-module email-module http-dirpy
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
