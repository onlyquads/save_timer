'''
# DESCRIPTION:
A maya script that creates a shelf button that changes over time
to remind user to save file.

# INSTALLATION:
Copy/Paste the save_timer folder to your maya20XX/scripts folder.
Use the following lines in maya python console or shelf button:

```from save_timer.save_timer import launch_save_timer; launch_save_timer()```

To launch it on maya startup do the following:
In the maya20XX/scripts folder, open or create the 'userSetup.py' file
add these lines to it:
```
maya.cmds.evalDeferred(
    "from save_timer.save_timer import SaveTimer; SaveTimer()",
    lowestPriority=True)
```
# COMPATIBILITY:
Maya 2022 and above

'''

import maya.cmds as mc
import maya.mel as mm
import maya.OpenMaya as om
from PySide2.QtWidgets import QWidget
from PySide2.QtCore import QTimer, QElapsedTimer

TOOLNAME = 'Save Timer'
TIMER_INTERVAL = 90000  # In milliseconds (1min30)
TIMER_BUTTON_WIDTH = 120

TIMER_STATES = [
    (-1.0, 'FILE NOT SAVED', (1.0, 0.0, 0.0)),
    (1.0, 'JUST NOW', (0.0, 1.0, 0.0)),
    (200.0, 'RECENTLY', (0.0, 0.5, 0.0)),
    (500.0, 'A FEW MIN AGO', (1.0, 0.451, 0.0)),
    (600.0, 'SAVE NOW!', (1.0, 0.0, 0.0))
    ]

# Insert the command you want to execute when save timer button is clicked
# SAVE_CMD = 'import maya.cmds as mc; mc.file(type="mayaAscii", save=True)'
SAVE_CMD = ''

SHELF_CALLBACK_NAMES = {
    'toggleShelfTabs',
    'shelfTabRefresh',
    'shelfTabChange'
}

save_timer = None


class SaveTimer(QWidget):
    def __init__(self):

        self.shelf_timer_button = None
        self.top_shelf = None
        self.current_shelf = None

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_button)
        self.elapsed_timer = QElapsedTimer()

        self.shelves_cleanup()
        self.create_button()

        # Register callbacks
        self.save_callback_id = om.MSceneMessage.addCallback(
            om.MSceneMessage.kAfterSave, self.on_scene_save)

        self.open_callback_id = om.MSceneMessage.addCallback(
            om.MSceneMessage.kAfterOpen, self.on_scene_open)

        self.new_callback_id = om.MSceneMessage.addCallback(
            om.MSceneMessage.kAfterNew, self.on_scene_new)

        self.exit_callback_id = om.MSceneMessage.addCallback(
            om.MSceneMessage.kMayaExiting, self.on_maya_exit)

        # This registers om callbacks mostly for user shelf interaction
        self.om_callbacks = om.MCommandMessage.addProcCallback(
            self.cmd_after_callback, None)

        print('Save Timer script has started')

    def on_scene_save(self, *args):
        # print('scene saved')
        if not self.timer.isActive():
            self.timer.start(TIMER_INTERVAL)
        self.elapsed_timer.start()
        self.update_button()

    def on_scene_open(self, *args):
        # print('scene opened')
        if not self.timer.isActive():
            self.timer.start(TIMER_INTERVAL)
        self.elapsed_timer.start()
        self.update_button()

    def on_scene_new(self, *args):
        # print('New scene')
        if self.timer.isActive():
            self.timer.stop()
        self.elapsed_timer.invalidate()
        self.update_button()

    def on_maya_exit(self, *args):
        self.shelves_cleanup()

    def get_current_state(self):
        elapsed_time = -1.0
        if self.timer.isActive():
            elapsed_time = float(self.elapsed_timer.elapsed() // 1000)
        # Check elapsed time against thresholds
        for threshold, text_label, bg_color in TIMER_STATES:
            if elapsed_time <= threshold:
                return text_label, bg_color
        # Stop our timer because we reached end of available states
        self.timer.stop()

    def update_button(self):
        if not self.shelf_timer_button:
            return
        label_text, bg_color = self.get_current_state()
        mc.shelfButton(
            self.shelf_timer_button,
            e=True,
            label=label_text,
            backgroundColor=bg_color
            )

    def create_button(self):
        shelf_top_level = mm.eval('$temp = $gShelfTopLevel')
        current_shelf = mc.tabLayout(
            shelf_top_level, query=True, selectTab=True)
        mc.setParent(current_shelf)
        label_text, bg_color = self.get_current_state()
        self.shelf_timer_button = mc.shelfButton(
            label=label_text,
            annotation='save timer click to save',
            style='textOnly',
            font='plainLabelFont',
            align='center',
            width=120,
            backgroundColor=bg_color,
            preventOverride=True,
            command=SAVE_CMD)
        mc.shelfButton(self.shelf_timer_button, edit=True, width=120)
        mc.shelfLayout(current_shelf, e=True, pos=(self.shelf_timer_button, 1))

    def get_button_path(self):
        shelf_top_level = mm.eval('$temp = $gShelfTopLevel')
        current_shelf = mc.tabLayout(
            shelf_top_level, query=True, selectTab=True)
        button_path = (
            f'{shelf_top_level}|{current_shelf}|{TOOLNAME}')
        return button_path

    def shelves_cleanup(self):
        if not self.current_shelf:
            self.top_shelf = mm.eval('$temp = $gShelfTopLevel;')
            self.current_shelf = mc.tabLayout(self.top_shelf, q=True, st=True)

        buttons = mc.shelfLayout(self.current_shelf, q=True, ca=True)

        if not buttons:
            return
        for button in buttons:
            if mc.objectTypeUI(button) != 'shelfButton':
                continue
            button_label = mc.shelfButton(button, q=True, label=True)
            if any(button_label == label[1] for label in TIMER_STATES):
                # last check if the shelf button exists before deleting it
                if mc.shelfButton(button, exists=True):
                    # print(f'Deleting button named : {button_label}')
                    mc.deleteUI(button)

        self.top_shelf = mm.eval('$temp = $gShelfTopLevel;')
        self.current_shelf = mc.tabLayout(self.top_shelf, q=True, st=True)

    def cmd_after_callback(
            self, proc_callback, invocation_id, bool, value, user_data):
        # Filter only positive callbacks
        if value != om.MCommandMessage.kMELProc or not bool:
            return
        # Filter only wanted callbacks
        if proc_callback in SHELF_CALLBACK_NAMES:
            self.shelf_tab_changed()

    def shelf_tab_changed(self):
        mc.evalDeferred(self.shelves_cleanup, lowestPriority=True)
        mc.evalDeferred(self.create_button, lowestPriority=True)
        mc.evalDeferred(self.update_button, lowestPriority=True)
        return

    def remove_callbacks(self):
        # Remove callbacks using their IDs
        om.MMessage.removeCallback(self.save_callback_id)
        om.MMessage.removeCallback(self.open_callback_id)
        om.MMessage.removeCallback(self.new_callback_id)
        om.MMessage.removeCallback(self.exit_callback_id)
        om.MMessage.removeCallback(self.om_callbacks)

    def kill_save_timer(self):
        self.remove_callbacks()
        mc.evalDeferred(self.shelves_cleanup, lowestPriority=True)
        if self.timer.isActive():
            self.timer.stop()

        self.shelf_timer_button = None
        self.top_shelf = None
        self.current_shelf = None

        global save_timer
        save_timer = None


def launch_save_timer():
    global save_timer
    if not save_timer:
        save_timer = SaveTimer()
        return
    save_timer.kill_save_timer()
