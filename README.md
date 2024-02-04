# Save Timer
## DESCRIPTION:
A maya script that creates a shelf button that changes over time to remind user to save file.

![](https://garcia-nicolas.com/wp-content/uploads/2024/02/save_timer_demo.gif)


## INSTALLATION:
Copy/Paste the save_timer folder to your maya20XX/scripts folder.
Use the following lines in maya python console or shelf button:

```
from save_timer.save_timer import SaveTimer; launch_save_time()
```

To launch it on maya startup do the following:
In the maya20XX/scripts folder, open or create the 'userSetup.py' file and add these lines to it:
```
maya.cmds.evalDeferred(
    "from save_timer.save_timer import SaveTimer; SaveTimer()",
    lowestPriority=True)
```
## COMPATIBILITY:
Maya 2022 and above
