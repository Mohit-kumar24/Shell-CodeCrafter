import sys
from app.shell.core.state import shell_state
from app.shell.executor.executor import process_command

def run_interactive_loop():
    """Read user input and pass to executor"""
    while shell_state.running:
        try:
            prompt_string=shell_state.prompt
            sys.stdout.write(prompt_string)
            sys.stdout.flush()  # To forcing input to appear quickly
            
            # Reading User Input , added newline with it
            raw_input = sys.stdin.readline()
            
            # Passing it to executor
            process_command(raw_input)
            
        except KeyboardInterrupt:
            # Handling Ctrl + C so it does not kill python Process
            sys.stdout.write("\n")
            sys.stdout.flush()  # To forcing input to appear quickly
            
        
        except EOFError:
            # Handle Ctrl+D (EOF)
            sys.stdout.write("\n")
            shell_state.running = False
            
            
        except Exception as e :
            sys.stderr.write(f"Shell execution error: {e}\n")

        # break   # Single Iteration
    return