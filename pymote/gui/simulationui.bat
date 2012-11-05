@echo off
if /I [%1]==[] goto all
if /I [%1]==[help] goto help


goto end

:help
Echo Compilation of simulationui.py and icons_rc.py
goto end

:all
echo Compilation of simulationui.py 
call pyuic4 simulation.ui -o simulationui.py
echo Compilation of icons_rc.py
call pyrcc4 icons.qrc -o icons_rc.py
goto end

:end
