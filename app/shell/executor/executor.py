# app/shell/core/executor/executor.py

import subprocess
import os
from app.shell.core.state import shell_state

def process_command(raw_command):
    "Execute a single command . Stage 1 : external commands only"
    
    # Removing whitespace
    command=raw_command.strip()
    
    if not command:
        return
    
    # Handling exit manually for now
    if command=='exit':
        shell_state.running=False
        return

    # Splitting into args [naive - no quoting yet]
    args=command.split()
    
    # Try to execute it
    try:
        result=subprocess.run(args,cwd=shell_state.cwd)
        shell_state.exit_code= result.returncode
    
    except FileNotFoundError:
        print(f"{args[0]}: command not found")
        shell_state.exit_code= 127
    
    except Exception as e :
        print(f"")
        shell_state.exit_code=1