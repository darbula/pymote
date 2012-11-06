@echo off 
REM To pin batch to taskbar first create a shortcut to your batch file.
REM Get into shortcut property and change target to : cmd.exe /C "path-to-your-batch".
REM Simply drag your new shortcut to the taskbar. It should now be pinnable.
REM Right click to shortcut in TaskBar and then right click to pymote and then click on 
REM Properties and remove cmd.exe /C part to get back to initial target
REM In porperties optionally change font, layout and turn on Quick Edit mode in Options

REM Set PYMOTE_ENV environment variable to a path to virtual_env
if NOT "%PYMOTE_ENV%" == "" ( call %PYMOTE_ENV%\Scripts\activate.bat )
ipython --pylab