#app/shell/core/state.py

from app.shell.utils.constant import (
    DEFAULT_PROMPT,
)

class ShellState:
    def __init__(self):
        self.prompt=DEFAULT_PROMPT
        
        
        




# Creating a single shell global instance 
shell_state=ShellState()