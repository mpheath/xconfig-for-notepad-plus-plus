@echo off
setlocal

:: About: Setup xconfig.
:: Install configuration may require admin.

:: Working directory is script directory.
cd /d "%~dp0"

:: Get root directory.
set /p "root=Root directory of notepad++.exe: " || exit /b 1
set "root=%root:"=%"

:: Check root directory contains notepad++.exe.
if not exist "%root%\notepad++.exe" (
    >&2 echo File notepad++.exe not found
    exit /b 1
)

:: Set paths and display them.
set "PythonScriptDir=%root%\plugins\PythonScript"

if exist "%root%\doLocalConf.xml" (
    echo Portable configuration detected
    set "ConfigDir=%root%\plugins\Config"
) else (
    echo Install configuration detected
    set "ConfigDir=%AppData%\plugins\Config"
)

echo Dirs to use:
echo   Config: "%ConfigDir%"
echo   PythonScript: "%PythonScriptDir%"

:: Get confirmation to continue.
set /p "reply=Continue? : [n|y] " || exit /b 1
if not "%reply%" == "y" exit /b 0

:: Check PythonScript is installed.
if not exist "%PythonScriptDir%\PythonScript.dll" (
    >&2 echo Require PythonScript
    exit /b 1
)

:: Check startup.py exist.
if not exist "%PythonScriptDir%\scripts\startup.py" (
    >&2 echo File startup.py not found
    exit /b 1
)

:: Make directories.
if not exist "%ConfigDir%\PythonScript\lib" (
    md "%ConfigDir%\PythonScript\lib"
)

if not exist "%ConfigDir%\PythonScript\scripts" (
    md "%ConfigDir%\PythonScript\scripts"
)

:: Copy files.
if exist "xconfig.properties" (
    if not exist "%ConfigDir%\xconfig.properties" (
        echo Copy "xconfig.properties"
        copy "xconfig.properties" "%ConfigDir%\xconfig.properties"
    )
)

if exist "xconfig.py" (
    if not exist "%ConfigDir%\PythonScript\lib\xconfig.py" (
        echo Copy "xconfig.py"
        copy "xconfig.py" "%ConfigDir%\PythonScript\lib\xconfig.py"
    )
)

if exist "ToggleChangeHistory.py" (
    if not exist "%ConfigDir%\PythonScript\scripts\ToggleChangeHistory.py" (
        echo Copy "ToggleChangeHistory.py"
        copy "ToggleChangeHistory.py" "%ConfigDir%\PythonScript\scripts\ToggleChangeHistory.py"
    )
)

if exist "XConfigUI.py" (
    if not exist "%ConfigDir%\PythonScript\scripts\XConfigUI.py" (
        echo Copy "XConfigUI.py"
        copy "XConfigUI.py" "%ConfigDir%\PythonScript\scripts\XConfigUI.py"
    )
)

:: Check if startup.py needs to be updated.
findstr /c:"import xconfig" "%PythonScriptDir%\scripts\startup.py" >nul

if errorlevel 1 (
    echo Update "startup.py" to import xconfig.py

    (
        echo:
        echo try:
        echo     import xconfig
        echo except ImportError:
        echo     pass
        echo else:
        echo     # Set settings for current buffer.
        echo     xconfig.reload(^)
        echo:
        echo     # Set settings on change of buffer...
        echo     notepad.callback(xconfig.reload, [NOTIFICATION.BUFFERACTIVATED,
        echo                                       NOTIFICATION.LANGCHANGED,
        echo                                       NOTIFICATION.WORDSTYLESUPDATED]^)
    ) >> "%PythonScriptDir%\scripts\startup.py"
)

:: Set PythonScript to run at Notepad++ startup.
if not exist "%ConfigDir%\PythonScriptStartup.cnf" (
    echo Create "PythonScriptStartup.cnf" to run ATSTARTUP

    (
        echo SETTING/STARTUP/ATSTARTUP
    ) > "%ConfigDir%\PythonScriptStartup.cnf"
)

echo done
