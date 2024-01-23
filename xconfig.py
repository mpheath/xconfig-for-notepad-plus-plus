# About: Set properties on each buffer
# ThisFile: plugins\Config\PythonScript\lib\xconfig.py
# DataFile: plugins\Config\xconfig.properties
# StartupFile: plugins\PythonScript\scripts\startup.py
#
# Add this fenced code section to startup.py to trigger the callback:
#
# ```
# try:
#     import xconfig
# except ImportError:
#     pass
# else:
#     # Set settings for current buffer.
#     xconfig.reload()
#
#     # Set settings on change of buffer...
#     notepad.callback(xconfig.reload, [NOTIFICATION.BUFFERACTIVATED,
#                                       NOTIFICATION.LANGCHANGED,
#                                       NOTIFICATION.WORDSTYLESUPDATED])
# ```
#
# Change PythonScript Initialisation from LAZY to ATSTARTUP.

from Npp import console, editor, notepad
import os
import sys

MARK_BOOKMARK = 20
SC_MARKNUM_HISTORY_REVERTED_TO_ORIGIN = 21
SC_MARKNUM_HISTORY_SAVED = 22
SC_MARKNUM_HISTORY_MODIFIED = 23
SC_MARKNUM_HISTORY_REVERTED_TO_MODIFIED = 24
INDICATOR_HISTORY_REVERTED_TO_ORIGIN_INSERTION = 36
INDICATOR_HISTORY_REVERTED_TO_ORIGIN_DELETION = 37
INDICATOR_HISTORY_SAVED_INSERTION = 38
INDICATOR_HISTORY_SAVED_DELETION = 39
INDICATOR_HISTORY_MODIFIED_INSERTION = 40
INDICATOR_HISTORY_MODIFIED_DELETION = 41
INDICATOR_HISTORY_REVERTED_TO_MODIFIED_INSERTION = 42
INDICATOR_HISTORY_REVERTED_TO_MODIFIED_DELETION = 43

# Normal operation should be quiet.
verbose = 0


if sys.version_info.major < 3:
    # Support for Python 2 editor.getChangeHistory and editor.setChangeHistory.

    import ctypes
    import ctypes.wintypes

    def _changeHistory(mode):
        SCI_SETCHANGEHISTORY = 2780
        SCI_GETCHANGEHISTORY = 2781

        LRESULT = ctypes.wintypes.LPARAM

        function_type = ctypes.CFUNCTYPE(LRESULT,
                                         ctypes.wintypes.HWND,
                                         ctypes.wintypes.UINT,
                                         ctypes.wintypes.WPARAM,
                                         ctypes.wintypes.LPARAM)

        scintilla_direct_function = function_type(editor.getDirectFunction())
        scintilla_direct_pointer = editor.getDirectPointer()

        if mode == 'get':
            def _get():
                value = scintilla_direct_function(scintilla_direct_pointer,
                                                  SCI_GETCHANGEHISTORY, 0, 0)
                return int(value)

            return _get
        elif mode == 'set':
            def _set(value):
                scintilla_direct_function(scintilla_direct_pointer,
                                          SCI_SETCHANGEHISTORY, value, 0)
            return _set

    editor.getChangeHistory = _changeHistory('get')
    editor.setChangeHistory = _changeHistory('set')
    del _changeHistory


def read():
    '''Read settings from file.'''

    if not os.path.isfile(config_file):
        if verbose:
            console.write('{}: Properties file does not exist.\n'
                          .format(__name__, key))
        return

    with open(config_file) as r:
        settings.clear()

        for line in r:
            line = line.strip()

            # Ignore empty lines and comment lines.
            if not line or line.startswith(('#', ';')):
                continue

            # Split key, value and append to the list.
            items = line.split('=', 1)

            if len(items) == 2:
                items = [s.strip() for s in items]

                if items[1]:
                    settings[items[0]] = items[1]


def reload(args=None):
    '''Callback function to reload settings.'''

    def hexadecimal(value):
        '''Hex string to RGB tuple of integers.'''

        if len(value) != 6:
            invalid_keys.append(key)
            return

        try:
            value = tuple(int(value[i:i+2], 16) for i in (0, 2, 4))
        except ValueError:
            value = None
            invalid_keys.append(key)

        return value


    def integer(value):
        '''String to integer.'''

        try:
            value = int(value)
        except ValueError:
            value = None
            invalid_keys.append(key)

        return value


    invalid_keys = []

    for key, value in settings.items():

        if key == 'backspace.unindents':
            value = integer(value)

            if value is not None:
                if value in range(2):
                    value = True if value else False
                    editor.setBackSpaceUnIndents(value)
                else:
                    invalid_keys.append(key)

        elif key == 'bookmark.colour':
            value = hexadecimal(value)

            if value is not None:
                editor.markerSetBack(MARK_BOOKMARK, value)

        elif key == 'bookmark.marker':
            value = integer(value)

            if value is not None:
                editor.markerDefine(MARK_BOOKMARK, value)

        elif key == 'caret.width':
            value = integer(value)

            if value is not None:
                if value > 0:
                    editor.setCaretWidth(value)
                else:
                    invalid_keys.append(key)

        elif key == 'change.history':
            value = integer(value)

            if value is not None:
                if value in (1, 3, 5, 7):
                    editor.setChangeHistory(value)
                else:
                    invalid_keys.append(key)

        elif key.startswith('change.history.colour.'):
            value = hexadecimal(value)

            if value is not None:
                if key.endswith('colour.modified'):
                    mark = SC_MARKNUM_HISTORY_MODIFIED
                    indic = (INDICATOR_HISTORY_MODIFIED_INSERTION,
                             INDICATOR_HISTORY_MODIFIED_DELETION)
                elif key.endswith('colour.reverted.modified'):
                    mark = SC_MARKNUM_HISTORY_REVERTED_TO_MODIFIED
                    indic = (INDICATOR_HISTORY_REVERTED_TO_MODIFIED_INSERTION,
                             INDICATOR_HISTORY_REVERTED_TO_MODIFIED_DELETION)
                elif key.endswith('colour.reverted.origin'):
                    mark = SC_MARKNUM_HISTORY_REVERTED_TO_ORIGIN
                    indic = (INDICATOR_HISTORY_REVERTED_TO_ORIGIN_INSERTION,
                             INDICATOR_HISTORY_REVERTED_TO_ORIGIN_DELETION)
                elif key.endswith('colour.saved'):
                    mark = SC_MARKNUM_HISTORY_SAVED
                    indic = (INDICATOR_HISTORY_SAVED_INSERTION,
                             INDICATOR_HISTORY_SAVED_DELETION)
                else:
                    mark = None

                if mark:
                    editor.markerSetFore(mark, value)
                    editor.markerSetBack(mark, value)

                    for i in indic:
                        editor.indicSetFore(i, value)

        elif key == 'change.history.indicator':
            value = integer(value)

            if value is not None:
                if value in range(23):
                    for i in (36, 38, 40, 42):
                        editor.indicSetStyle(i, value)
                else:
                    invalid_keys.append(key)


        elif key.startswith('change.history.marker.'):
            value = integer(value)

            if value is not None:
                if key == 'change.history.marker.modified':
                    mark = SC_MARKNUM_HISTORY_MODIFIED
                elif key == 'change.history.marker.reverted.modified':
                    mark = SC_MARKNUM_HISTORY_REVERTED_TO_MODIFIED
                elif key == 'change.history.marker.reverted.origin':
                    mark = SC_MARKNUM_HISTORY_REVERTED_TO_ORIGIN
                elif key == 'change.history.marker.saved':
                    mark = SC_MARKNUM_HISTORY_SAVED
                else:
                    mark = None

                if mark:
                    editor.markerDefine(mark, value)

        elif key == 'fold.flags':
            value = integer(value)

            if value is not None:
                line_margin = 0
                width = editor.getMarginWidthN(line_margin)

                if 64 & value or 128 & value:
                    if width != 0 and width != 128:
                        editor.setMarginWidthN(line_margin, 0)
                        width = editor.getMarginWidthN(line_margin)

                    if width == 0:
                        editor.setMarginWidthN(line_margin, 128)
                        width = editor.getMarginWidthN(line_margin)

                    if width == 128:
                        editor.setFoldFlags(value)
                else:
                    editor.setFoldFlags(value)

        elif key == 'horizontal.scroll.width':
            value = integer(value)

            if value is not None:
                editor.setScrollWidth(value)

        elif key == 'horizontal.scroll.width.tracking':
            value = integer(value)

            if value is not None:
                value = True if value else False
                editor.setScrollWidthTracking(value)

        elif key == 'tab.indents':
            value = integer(value)

            if value is not None:
                if value in range(2):
                    value = True if value else False
                    editor.setTabIndents(value)
                else:
                    invalid_keys.append(key)

        elif key == 'technology':
            value = integer(value)

            if value is not None:
                if value in range(4):
                    editor.setTechnology(value)
                else:
                    invalid_keys.append(key)

        elif key == 'whitespace.size':
            value = integer(value)

            if value is not None:
                editor.setWhitespaceSize(value)

        elif key == 'wrap.indent.mode':
            value = integer(value)

            if value is not None:
                if value in range(4):
                    editor.setWrapIndentMode(value)
                else:
                    invalid_keys.append(key)

        elif key == 'wrap.style':
            value = integer(value)

            if value is not None:
                if value in range(4):
                    editor.setWrapMode(value)
                else:
                    invalid_keys.append(key)

        elif key == 'wrap.visual.flags':
            value = integer(value)

            if value is not None:
                if value in range(4):
                    editor.setWrapVisualFlags(value)
                else:
                    invalid_keys.append(key)

        elif key == 'wrap.visual.flags.location':
            value = integer(value)

            if value is not None:
                if value in range(4):
                    editor.setWrapVisualFlagsLocation(value)
                else:
                    invalid_keys.append(key)

        elif key == 'wrap.visual.startindent':
            value = integer(value)

            if value is not None:
                editor.setWrapStartIndent(value)

        else:
            editor.setProperty(key, value)

    for key in invalid_keys:
        if verbose:
            console.write('{}: Removing {} key as to value error.\n'
                          .format(__name__, key))
        del settings[key]


def toggleChangeHistory(two_way=True):
    '''Toggle change.history.

    two_way: True 2-way, False 4-way.
    '''

    value = editor.getChangeHistory()

    if two_way:
        value = 1 if value != 1 else 3
    else:
        value = (value + 2) if value < 7 else 1

    settings['change.history'] = value
    reload()


def view():
    '''View settings as config style.'''

    for key, value in settings.items():
        console.write('{} = {}\n'.format(key, value))


# Path to the file with the settings.
config_file = os.path.join(notepad.getPluginConfigDir(), 'xconfig.properties')

# Get the settings.
settings = {}
read()
