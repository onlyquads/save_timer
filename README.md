# Save Timer
## Description:
A maya script that creates a shelf button that changes over time to remind user to save file. Whenever you change shelf tab, the button is deleted from the previous shelf and recreated on the current visible shelf.

![](https://garcia-nicolas.com/wp-content/uploads/2024/02/save_timer_demo.gif)


## Installation:
First Copy/Paste the save_timer folder to your maya20XX/scripts folder.

Option 1: Use the following python code in maya python console or as shelf button. It will act like a toggle ON/OFF button:

```python
from save_timer.save_timer import launch_save_timer; launch_save_timer()
```

Option 2 (best): Launch it automatically on maya startup:
In the maya20XX/scripts folder, open or create the 'userSetup.py' file and add these lines to it:
```python
import maya.cmds as mc
if not mc.about(batch=True):
    mc.evalDeferred(
        "from save_timer.save_timer import SaveTimer; SaveTimer()",
        lowestPriority=True)
```


Option 3 (with user options): Launch it automatically on maya startup with
message box to ask if user want's it or not and set this preference
automatically for next maya sessions:
```python
import maya.cmds as mc
if not mc.about(batch=True):
    mc.evalDeferred(
        "from save_timer.save_timer import auto_start_save_timer; auto_start_save_timer()",
        lowestPriority=True)
```

If you want the user to be able to get the message box back to change option:
```python
from save_timer.save_timer import show_save_timer_startup_message;
show_save_timer_startup_message()
```
## Compatibility:
Maya 2022 and above

