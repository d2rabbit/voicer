@echo off
setlocal

:: 设置 Python 脚本的名称
set "SCRIPT_NAME=main.py"

:: 使用 wmic 查找并终止进程
echo 正在查找并关闭 %SCRIPT_NAME% 相关的 Python 进程...
wmic process where "commandline like '%%%SCRIPT_NAME%%%' and name='pythonw.exe'" call terminate

echo 脚本执行完毕。
:: 等待 2 秒后自动退出
timeout /t 2 >nul
endlocal
exit