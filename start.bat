::[Bat To Exe Converter]
::
::YAwzoRdxOk+EWAjk
::fBw5plQjdCyDJGyX8VAjFJOkkYxy4VeKD7YI/fr+/NaGqEMQR69nf4fcwvnecLFd40brFQ==
::YAwzuBVtJxjWCl3EqQJhSA==
::ZR4luwNxJguZRRmX/FcxIXs=
::Yhs/ulQjdF+5
::cxAkpRVqdFKZSzk=
::cBs/ulQjdF+5
::ZR41oxFsdFKZSDk=
::eBoioBt6dFKZSDk=
::cRo6pxp7LAbNWATEpCI=
::egkzugNsPRvcWATEpCI=
::dAsiuh18IRvcCxnZtBJQ
::cRYluBh/LU+EWAnk
::YxY4rhs+aU+JeA==
::cxY6rQJ7JhzQF1fEqQJQ
::ZQ05rAF9IBncCkqN+0xwdVs0
::ZQ05rAF9IAHYFVzEqQJQ
::eg0/rx1wNQPfEVWB+kM9LVsJDGQ=
::fBEirQZwNQPfEVWB+kM9LVsJDGQ=
::cRolqwZ3JBvQF1fEqQJQ
::dhA7uBVwLU+EWDk=
::YQ03rBFzNR3SWATElA==
::dhAmsQZ3MwfNWATElA==
::ZQ0/vhVqMQ3MEVWAtB9wSA==
::Zg8zqx1/OA3MEVWAtB9wSA==
::dhA7pRFwIByZRRnk
::Zh4grVQjdCqDJFqL8GseDydCQw2BOVS7FaYV+/z64f64tV0hduMrR7vU5ZGWJd8w5UvycIQ502gUndMJbA==
::YB416Ek+ZG8=
::
::
::978f952a14a936cc963da21a135fa983
@echo off
setlocal

:: 设置 Python 路径和脚本路�?
set "PYTHON_PATH=%~dp0WPy64-310110\python-3.10.11.amd64\pythonw.exe"
set "SCRIPT_PATH=%~dp0main.py"
set "LOG_PATH=%~dp0log\output.log"

:: 创建日志目录（如果不存在�?
if not exist "%~dp0log" mkdir "%~dp0log"

:: 使用 start 命令来隐藏窗口并运行 Python 脚本
start "" /B "%PYTHON_PATH%" "%SCRIPT_PATH%" > "%LOG_PATH%" 2>&1"

endlocal