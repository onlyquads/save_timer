'''
# DESCRIPTION:
This script will add a save reminder button shelf on the current active
maya shelf. This timer will give a hint about the last 'file save' action
and remind you to save if the last save is a couple of minutes ago.

# TODO: -Add ShelfTab changed behavior: remove existing button + create button

# INSTALLATION:
add these lines to userSetup.py:

import maya.cmds as mc
mc.evalDeferred(
    "from save_timer.save_timer import SaveTimer; SaveTimer()",
    lowestPriority=True)

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
DEFAUT_STATE = ['File not saved', (1.0, 0.0, 0.0)]

TIMER_STATES = [
    (1.0, 'JUST NOW', (0.0, 1.0, 0.0)),
    (120.0, 'RECENTLY', (0.0, 0.5, 0.0)),
    (300.0, 'A FEW MIN AGO', (1.0, 0.451, 0.0)),
    (480.0, 'SAVE NOW!', (1.0, 0.0, 0.0))
    ]


class SaveTimer(QWidget):
    def __init__(self):
        self.button_name = DEFAUT_STATE[0]

        self.timer = QTimer()
        self.timer.timeout.connect(self.check_timer)
        self.elapsed_timer = QElapsedTimer()

        self.remove_from_shelf()
        self.create_button()

        # Register callbacks
        om.MSceneMessage.addCallback(
            om.MSceneMessage.kAfterSave, self.on_scene_save)

        om.MSceneMessage.addCallback(
            om.MSceneMessage.kAfterOpen, self.on_scene_open)

        om.MSceneMessage.addCallback(
            om.MSceneMessage.kAfterNew, self.on_scene_new)

        print('Save Timer Loaded')

    def on_scene_save(self, *args):
        # print('scene saved')
        if not self.timer.isActive():
            self.timer.start(TIMER_INTERVAL)
        self.elapsed_timer.start()
        self.check_timer()

    def on_scene_open(self, *args):
        print('scene opened')
        if not self.timer.isActive():
            self.timer.start(TIMER_INTERVAL)
        self.elapsed_timer.start()
        self.check_timer()

    def on_scene_new(self, *args):
        # print('New scene')
        self.remove_from_shelf()
        self.create_button()
        if self.timer.isActive():
            self.timer.stop()
        self.update_button(DEFAUT_STATE[0], DEFAUT_STATE[1])

    def check_timer(self):
        # print('check timer')
        elapsed_time = float(self.elapsed_timer.elapsed() // 1000)
        # Check elapsed time against thresholds
        for threshold, text_label, bg_color in TIMER_STATES:
            if elapsed_time <= threshold:
                self.update_button(text_label, bg_color)
                return
        # print('stop timer')
        self.timer.stop()

    def update_button(self, text_label, bg_color):
        # print('Button updated')
        mc.shelfButton(
            self.shelf_timer_button,
            e=True,
            label=text_label,
            backgroundColor=bg_color
            )

    def create_button(self):
        # print('Button Created')
        command = 'print("Timer button clicked")'
        shelf_top_level = mm.eval('$temp = $gShelfTopLevel')
        current_shelf = mc.tabLayout(
            shelf_top_level, query=True, selectTab=True)
        mc.setParent(current_shelf)
        self.shelf_timer_button = mc.shelfButton(
            label=self.button_name,
            useTemplate=TIMER_STATES[0][1],
            annotation='save timer click to save',
            style='textOnly',
            font='plainLabelFont',
            align='center',
            width=120,
            backgroundColor=(1, 0, 0),
            preventOverride=True,
            command=command)
        mc.shelfButton(self.shelf_timer_button, edit=True, width=120)
        mc.shelfLayout(current_shelf, e=True, pos=(self.shelf_timer_button, 1))

    def get_button_path(self):
        shelf_top_level = mm.eval('$temp = $gShelfTopLevel')
        current_shelf = mc.tabLayout(
            shelf_top_level, query=True, selectTab=True)
        button_path = (
            f'{shelf_top_level}|{current_shelf}|{TOOLNAME}')
        return button_path

    def remove_from_shelf(self):
        top_shelf = mm.eval(
            'global string $top_shelf; $temp = $gShelfTopLevel;')
        currentShelf = mc.tabLayout(top_shelf, q=True, st=True)
        buttons = mc.shelfLayout(currentShelf, q=True, ca=True)
        # Combine all the possible save timer button names in a list
        timer_names = [self.button_name]
        for i in TIMER_STATES:
            timer_names.append(i[1])

        for button in buttons:
            button_name = mc.shelfButton(button, q=True, label=True)
            if any(button_name == name for name in timer_names):
                # last check if the shelf button exists before deleting it
                if mc.shelfButton(button, exists=True):
                    mc.deleteUI(button)

    def on_shelf_tab_change(self):
        # print('shelf tab changed!')
        return
