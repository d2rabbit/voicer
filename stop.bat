@echo off
setlocal

:: ���� Python �ű�������
set "SCRIPT_NAME=main.py"

:: ʹ�� wmic ���Ҳ���ֹ����
echo ���ڲ��Ҳ��ر� %SCRIPT_NAME% ��ص� Python ����...
wmic process where "commandline like '%%%SCRIPT_NAME%%%' and name='pythonw.exe'" call terminate

echo �ű�ִ����ϡ�
:: �ȴ� 2 ����Զ��˳�
timeout /t 2 >nul
endlocal
exit