@echo off

REM set py27_dir=D:\bin\Python27
set py27_dir=C:\Users\rzfwch\bin\Python27

if %1 == u goto ui:
if %1 == r goto res:
if %1 == e goto exe:

goto EOF:

:ui
echo make ui ...
%py27_dir%\Lib\site-packages\PyQt4\pyuic4.bat -x res\main.ui -o main_ui.py
%py27_dir%\Lib\site-packages\PyQt4\pyuic4.bat -x res\downloader.ui -o downloader_ui.py
echo done
goto EOF:

:res
echo make res ...
%py27_dir%\Lib\site-packages\PyQt4\pyrcc4.exe res\res.qrc -o res_rc.py
echo done
goto EOF:

:exe
echo make exe ...
setup.py py2exe
echo done
goto EOF:

:EOF

pause

@echo on