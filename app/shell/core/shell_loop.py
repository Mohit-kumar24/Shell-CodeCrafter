import sys
from app.shell.core.state import shell_state

def run_interactive_loop():
    """The core REPL (Read-Eval-Print Loop) driving your python shell."""
    while True:
        try:
            prompt_string=shell_state.prompt
            sys.stdout.write(prompt_string)
        except KeyboardInterrupt:
            # Handling Ctrl + C so it does not kill python Process
            sys.stdout.write("\n")
        
        except Exception as e :
            sys.stderr.write(f"Shell execution error: {e}\n")

        break   # Single Iteration
    return