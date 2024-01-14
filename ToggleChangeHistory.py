from Npp import notepad

# True 2-way, False 4-way
xconfig.toggleChangeHistory(True)

# Activate current buffer to cause the ui to update.
notepad.activateBufferID(notepad.getCurrentBufferID())
