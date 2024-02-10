# Save Timer
## Description:
A maya script that creates a shelf button that changes over time to remind user to save file.

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
## Compatibility:
Maya 2022 and above
