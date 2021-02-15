@echo off
git pull
python setup.py sdist bdist_wheel

call :output "python install.py"
exit /b
:output
for /f "tokens=* useback" %%a in (`%~1`) do set "output=%%a"

pip install dist/%output%