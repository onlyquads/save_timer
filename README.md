# Save Timer
# DESCRIPTION:
A maya script that creates a shelf button that changes over time
to remind user to save file.

# INSTALLATION:
add these lines to userSetup.py:

```
import maya.cmds as mc
mc.evalDeferred(
    "from save_timer.save_timer import SaveTimer; SaveTimer()",
    lowestPriority=True)
```

# COMPATIBILITY:
Maya 2022 and above
