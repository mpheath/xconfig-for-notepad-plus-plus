'''A Notepad++ PythonScript User Interface to access settings from xconfig.py.

Properties set from the UI will be applied in runtime which are not saved.

A view widget shows settings applied which can be manually copied into
xconfig.properties.

The UI is optional as xconfig.py and xconfig.properties can apply settings
at PythonScript startup. Set PythonScript Initialisation from "Lazy" to
"AtStartup" to run xconfig.py at Notepad++ startup. The UI code will error
if xconfig.py has not been run at startup.
'''

import os
import sys

if sys.version_info.major < 3:
    import Tkinter as tkinter
    import ttk
    tkinter.ttk = ttk
    del ttk
    editor.getChangeHistory = xconfig.editor.getChangeHistory
    editor.setChangeHistory = xconfig.editor.setChangeHistory
else:
    import tkinter
    import tkinter.ttk

# Normal operation should be quiet.
verbose = 0


class XConfigUI():
    def __init__(self):
        '''Create the window.'''

        self.tk =o= tkinter.Tk()
        o.title('XConfigUI')
        o.geometry('450x400')
        o.resizable(True, False)
        o.minsize(450, 400)
        o.maxsize(950, 400)
        self.create_widgets()
        o.mainloop()


    def create_widgets(self):
        '''Create all widgets.'''

        CONTROL = 4

        def readonly_text(event):

            # Disable keys except for Ctrl+A and Ctrl+C.
            if not (event.state == CONTROL and event.keysym in ('a', 'c')):
                return 'break'

        def validate_entry(value):

            # Get selected listbox item.
            index = self.listbox.curselection()

            if not index:
                return False

            key = self.listbox.get(index[0])

            # Allow empty character.
            if not value:
                return True

            # Allow hex number.
            if '.colour' in key:
                if len(value) > 6:
                    return False

                for item in value:
                    if item.lower() not in '0123456789abcdef':
                        return False

                return True

            # Restrict to integers unless defined other.
            if key.startswith(('caret.', 'change.history',
                               'fold.', 'lexer.', 'wrap.')):

                # Allow any character for these properties.
                if key in ('lexer.as.comment.character',
                           'lexer.asm.comment.delimiter'):
                    return True

                # Allow integers.
                if value.isdigit():
                    return True

                return False

            elif key in ('asp.default.language',
                         'autocomplete.visible.item.count',
                         'backspace.unindents',
                         'bookmark.marker',
                         'fold',
                         'horizontal.scroll.width',
                         'horizontal.scroll.width.tracking',
                         'idle.styling',
                         'html.tags.case.sensitive',
                         'nsis.ignorecase',
                         'nsis.uservars',
                         'ps.level',
                         'sql.backslash.escapes',
                         'styling.within.preprocessor',
                         'tab.draw.mode',
                         'tab.timmy.whinge.level',
                         'technology',
                         'whitespace.size'):

                # Allow integers.
                if value.isdigit():
                    return True

                return False

            # Allow any character for unspecified properties.
            if verbose:
                print(key, 'allows any character')

            return True

        register_entry = (self.tk.register(validate_entry), '%P')
        self.file_settings = self.read_settings()
        self.file_keys = sorted(self.file_settings.keys())

        # Entry for listbox filtering.
        self.entry =o= tkinter.Entry()
        o.place(x=10, y=10, w=430)
        o.bind('<Key>', self.update_listbox)

        # Listbox of property items.
        self.listbox =o= tkinter.Listbox()
        o.place(x=10, y=35, w=430, h=300)
        o.insert('end', *self.file_keys)
        o.bind('<<ListboxSelect>>', self.on_listbox)
        o.activate(0)

        # Scrollbar for the listbox.
        scrollbar =o= tkinter.Scrollbar(o)
        o.pack(side='right', fill='both')
        o.config(command=self.listbox.yview)
        self.listbox.config(yscrollcommand=o.set)

        # Label to display section of an existing value.
        self.label_section =o= tkinter.Label(borderwidth=1, relief='sunken',
                                             anchor='w')
        o.place(x=20, y=359, w=80)

        # Label to display origin of an existing value.
        self.label_origin =o= tkinter.Label(borderwidth=1, relief='sunken',
                                            anchor='w')
        o.place(x=120, y=359, w=80)

        # Entry for property value to be set.
        self.entry_value =o= tkinter.Entry(validatecommand=register_entry,
                                           validate='key')
        o.place(x=220, y=359, w=80)

        # Button to set property value.
        self.button_set =o= tkinter.Button(command=self.on_button_set,
                                           text='Set')
        o.place(x=330, y=355, w=80)

        # Text for description of selected property item.
        self.text_desc =o= tkinter.Text()
        o.place(x=455, y=10, w=480, h=180)
        o.bind('<Key>', readonly_text)
        o.insert('1.0', 'Select an item from the {} items in the list.'
                        .format(len(self.file_keys)))

        # Text to view set properties.
        self.view =o= tkinter.Text()
        o.place(x=455, y=200, w=480, h=180)
        o.bind('<Key>', readonly_text)

        # Size grip to assist with window resize.
        sizegrip =o= tkinter.ttk.Sizegrip(cursor='sb_h_double_arrow')
        o.place(relx=1, rely=1, anchor='se')

        # Update view and focus the first Entry.
        self.update_view()
        self.entry.focus_set()


    def on_button_set(self):
        '''Set the selected property on pressed Set Button.'''

        # Get selected listbox item.
        index = self.listbox.curselection()

        if not index:
            return

        key = self.listbox.get(index[0])

        # Get entry value.
        value = self.entry_value.get()

        if value:
            xconfig.settings[key] = value
            xconfig.reload()
        else:
            if key in xconfig.settings:
                del xconfig.settings[key]
                xconfig.reload()

        # Update label and entry.
        self.update_label(key)
        self.update_view()

        # Activate buffer to trigger event.
        notepad.activateBufferID(notepad.getCurrentBufferID())


    def on_listbox(self, event):
        '''Update other widget values on Listbox selection.'''

        # Get selected listbox item.
        index = event.widget.curselection()

        if not index:
            return

        key = event.widget.get(index[0])
        value = ''
        self.text_desc.delete('1.0', 'end')
        self.entry_value.delete('0', 'end')

        # Section from file.
        section = self.file_settings[key].get('section')
        self.label_section.config(text=section)

        # Description from file.
        desc = self.file_settings[key].get('desc')
        self.text_desc.insert('1.0', desc)

        # Update label, entry and view.
        value = self.update_label(key)

        if value:
            self.entry_value.insert('0', value)

        self.update_view()


    def read_settings(self):
        '''Read xconfig.properties into a dictionary with descriptions.
        Return: Dictionary
        '''

        config_file = os.path.join(notepad.getPluginConfigDir(),
                                   'xconfig.properties')
        desc = ''
        dic = {}
        section = ''

        with open(config_file) as r:
            for line in r:
                line = line.strip()

                if not line or line.startswith('##'):
                    continue

                if line.startswith('['):
                    section = line[1:-1]

                # Get property description.
                if line.startswith('#'):
                    desc = line[1:].strip()
                    continue

                # Get properties keys and values.
                parts = line.split('=', 1)

                if len(parts) == 2:
                    key = parts[0].strip()
                    value = parts[1].strip()

                    dic[key] = {'desc': desc,
                                'section': section,
                                'value': value}

        return dic


    def update_label(self, key):
        '''Update Label with value of "memory", "defined" or "".'''

        # Set as memory.
        value = xconfig.settings.get(key)

        if value:
            self.label_origin.config(text='memory')
            return value

        # Set as defined.
        if key == 'autocomplete.visible.item.count':
            value = str(editor.autoCGetMaxHeight())
        elif key == 'backspace.unindents':
            value = editor.getBackSpaceUnIndents()
            value = '1' if value else '0'
        elif key == 'bookmark.colour':
            value = ''
        elif key == 'bookmark.marker':
            marker = xconfig.MARK_BOOKMARK
            value = str(editor.markerSymbolDefined(marker))
        elif key == 'caret.additional.blinks':
            value = editor.getAdditionalCaretsBlink()
            value = '1' if value else '0'
        elif key == 'caret.line.visible.always':
            value = editor.getCaretLineVisibleAlways()
            value = '1' if value else '0'
        elif key == 'caret.width':
            value = str(editor.getCaretWidth())
        elif key == 'change.history':
            value = str(editor.getChangeHistory())
        elif key.startswith('change.history.colour.'):
            value = ''
        elif key == 'change.history.indicator':
            value = ''
        elif key == 'change.history.marker.modified':
            marker = xconfig.SC_MARKNUM_HISTORY_MODIFIED
            value = str(editor.markerSymbolDefined(marker))
        elif key == 'change.history.marker.reverted.modified':
            marker = xconfig.SC_MARKNUM_HISTORY_REVERTED_TO_MODIFIED
            value = str(editor.markerSymbolDefined(marker))
        elif key == 'change.history.marker.reverted.origin':
            marker = xconfig.SC_MARKNUM_HISTORY_REVERTED_TO_ORIGIN
            value = str(editor.markerSymbolDefined(marker))
        elif key == 'change.history.marker.saved':
            marker = xconfig.SC_MARKNUM_HISTORY_SAVED
            value = str(editor.markerSymbolDefined(marker))
        elif key == 'fold.flags':
            value = ''
        elif key == 'horizontal.scroll.width':
            value = str(editor.getScrollWidth())
        elif key == 'horizontal.scroll.width.tracking':
            value = editor.getScrollWidthTracking()
            value = '1' if value else '0'
        elif key == 'idle.styling':
            value = str(editor.getIdleStyling())
        elif key == 'tab.draw.mode':
            value = str(editor.getTabDrawMode())
        elif key == 'technology':
            value = str(editor.getTechnology())
        elif key == 'whitespace.size':
            value = str(editor.getWhitespaceSize())
        elif key == 'wrap.indent.mode':
            value = str(editor.getWrapIndentMode())
        elif key == 'wrap.style':
            value = str(editor.getWrapMode())
        elif key == 'wrap.visual.flags':
            value = str(editor.getWrapVisualFlags())
        elif key == 'wrap.visual.flags.location':
            value = str(editor.getWrapVisualFlagsLocation())
        elif key == 'wrap.visual.startindent':
            value = str(editor.getWrapStartIndent())
        else:
            if verbose:
                if self.file_settings[key]['section'] != 'lexer':
                    print(key, 'is not a lexer setting')

            value = str(editor.getProperty(key))

        if value:
            self.label_origin.config(text='defined')
            return value

        # Set as none.
        self.label_origin.config(text='')


    def update_listbox(self, event):
        '''Update Listbox to match the substring of the Entry text.'''

        text = self.entry.get()

        # Update text if ANSI or backspace key.
        if event.keycode >= 32 and event.keycode <= 126:
            text += event.char
        elif event.keycode == 8:
            text = text[:-1]

        # Insert new items into Listbox.
        self.listbox.delete('0', 'end')

        if text:

            # By section name else by property name.
            if text.startswith('['):
                text = text[1:].lstrip()

                for key in self.file_keys:
                    if text.lower() in self.file_settings[key].get('section'):
                        self.listbox.insert('end', key)
            else:
                for key in self.file_keys:
                    if text.lower() in key.lower():
                        self.listbox.insert('end', key)
        else:

            # All property names.
            self.listbox.insert('end', *self.file_keys)


    def update_view(self):
        '''Update view from the xconfig.settings dictionary.'''

        self.view.delete('1.0', 'end')

        for key, value in xconfig.settings.items():
            self.view.insert('end', '{} = {}\n'.format(key, value))


if __name__ == '__main__':
    XConfigUI()
