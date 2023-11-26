from setuptools import setup, find_packages
import os

def package_files(directory):
    paths = []
    for (path, directories, filenames) in os.walk(directory):
        for filename in filenames:
            paths.append(os.path.join('..', path, filename))
    return paths
    
extra_files = package_files('nuisco/templates')

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name='nuisco',
    version='0.2.3',
    description='A faster and more customizable compiler based on nuitka',
    author='Cariel Becker',
    license='GPL-3.0',
    packages=find_packages(),
    python_requires='<3.12',#'<=3.11.6',
    install_requires=[
        'nuitka==1.8.4',
        'aplustools'
    ],
    entry_points={
        'console_scripts': [
            'nuisco = nuisco.main:console_script',
        ],
    },
    long_description=long_description,
    long_description_content_type="text/markdown",  # Indicate the content type (text/markdown, text/plain, text/x-rst)
    setup_requires=['pytest-runner'],
    tests_require=['pytest==4.4.1'],
    test_suite='tests',
    package_data={
        'nuisco': ['compile_libraries_v2.3.exe'] + extra_files,#, 'templates/*.json', 'templates/*/*'],
    }
)
