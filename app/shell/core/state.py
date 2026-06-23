# app/shell/core/state.py  
import os
from app.shell.utils.constant import (
    DEFAULT_PROMPT,
)

class ShellState:
    def __init__(self):
        self.prompt    = DEFAULT_PROMPT
        self.running   = True
        self.env       = {}
        self.cwd       = os.getcwd()
        self.exit_code = 0



# Creating a single shell global instance 
shell_state=ShellState()