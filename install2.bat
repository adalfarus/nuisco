@echo off
for %%F in (dist\*.whl) do (
    py -3.11 -m pip uninstall "%%F" -y
    py -3.11 -m pip install "%%F"
)
pause
