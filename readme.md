# xconfig for Notepad++


## About

Sets optional properties for Lexilla lexers and
properties for Scintilla.

Compatible with PythonScript 2 and 3.


## Details

Minimal use of xconfig is *xconfig.py* and *xconfig.properties*.
The latter file contains the permanent settings.
These settings are applied at startup by *xconfig.py*.

An extra option is *XConfigUI.py* which requires the additional *tkinter* package.
This script only handles the runtime settings in memory.
These settings are applied during the running instance of Notepad++.

More details about the optional UI can be viewed on the [ui page](ui/readme.md) .

Another extra option is *ToggleChangeHistory.py* which might help with
a requested feature to toggle Change History markers. The function is
in *xconfig.py* to keep the Global namespace clean so minimal code is
in *ToggleChangeHistory.py*. PythonScript allows a script to be an
icon in the toolbar, so can make it easy to toggle from there.

Fold settings usually apply at opening of a buffer, so the UI may
only have an effect with fold settings on new opened files.
At startup, all buffers are opened so fold settings apply ok at that time.
Some options like *fold.compact* or *fold.cpp.comment.explicit* work ok
with toggling during runtime so success on each fold property may vary.


## Setup

Check first that PythonScript is installed by Plugin Admin or download from
the site link below to manually install and if using the UI, go to

https://github.com/bruderstein/PythonScript/releases

and download a file like *PythonScript_TclTk_2.0.0.0_x64.zip* to get
the tkinter library. Note the TclTk which is short for Tcl tkinter.

PythonScript 3 should work well too if prefered though may not be in
Plugin Admin yet so download and manually install.

Manual setup of xconfig might be a challenge to some, though once done
then everything should be good.

If prefer a scripted xconfig setup, see *setup.cmd*. May need to run as admin
for an installed Notepad++ configuration so that *startup.py* can be updated.

For portable Notepad++ in root directory:

 1. Copy *xconfig.properties* to `plugins\Config\xconfig.properties` .
 2. Make dir `plugins\Config\PythonScript\lib` if not exist
    and copy *xconfig.py*
    to `plugins\Config\PythonScript\lib\xconfig.py` .
 3. Create file `plugins\Config\PythonScript\scripts\startup.py` if not exist
    and append this code to the end:

    ```py
    try:
        import xconfig
    except ImportError:
        pass
    ```

 4. Optionally, copy `XConfigUI.py` to
    `plugins\Config\PythonScript\scripts\XConfigUI.py` .
 5. Optionally, copy `ToggleChangeHistory.py` to
    `plugins\Config\PythonScript\scripts\ToggleChangeHistory.py` .


For installed Notepad++, paths are different:

 1. Copy *xconfig.properties* to `%AppData%\Notepad++\plugins\Config\xconfig.properties` .
 2. Make dir `%AppData%\Notepad++\plugins\Config\PythonScript\lib` if not exist
    and copy *xconfig.py*
    to `%AppData%\Notepad++\plugins\Config\PythonScript\lib\xconfig.py` .
 3. Create file `%AppData%\Notepad++\plugins\PythonScript\scripts\startup.py`
    if not exist and append this code to the end:

    Append code above!

 4. Optionally, copy `XConfigUI.py` to
    `%AppData%\Notepad++\plugins\Config\PythonScript\scripts\XConfigUI.py` .
 5. Optionally, copy `ToggleChangeHistory.py` to
    `%AppData%\Notepad++\plugins\Config\PythonScript\scripts\ToggleChangeHistory.py` .

Change PythonScript Initialisation from LAZY to ATSTARTUP so that
the settings are applied at the startup of Notepad++.


## Properties

Edit *xconfig.properties* to change property settings to be loaded at
Notepad++ startup. Most properties only support integer values.

So if you want the `change.history` property to startup as Indicators
and Markers, then change:

```ini
change.history=
```

to

```ini
change.history=7
```

and save. That is all it takes to change a property setting.

A property value that is invalid by going out of bounds, incorrect type...
might be ignored or possibly removed from the dictionary of settings.

To change at runtime, without the UI, open PythonScript console and type
into the run box `xconfig.settings['change.history']=1`.
May need to change tabs or similar event to update the buffer or use
`notepad.activateBufferID(notepad.getCurrentBufferID())`
which is getting a bit long to handle outside of a script.
That is why the UI was created to make runtime changes easier.
