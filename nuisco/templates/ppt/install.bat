@echo off
for %%F in (dist\*.whl) do (
    py -3.11 -m pip install "%%F" --force-reinstall
)
pause
