from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name='nuisco',
    version='0.1.0',
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
            'nic_compile = nic.build:build_main',
        ],
    },
    long_description=long_description,
    long_description_content_type="text/markdown",  # Indicate the content type (text/markdown, text/plain, text/x-rst)
    setup_requires=['pytest-runner'],
    tests_require=['pytest==4.4.1'],
    test_suite='tests',
    package_data={
        'nic': ['compile_libraries_v2.3.exe'],
    }
)
