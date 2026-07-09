# app/shell/builtin/exit.py
import sys

def builtin_exit(args,shell_state)->int:
    """Exit the shell with optional numeric exit code."""
    
    if not args:
        shell_state.exit_code=0 # Success    
    else:
        try:
            shell_state.exit_code=(int(args[0]))
        except ValueError:
            sys.stderr.write(f"exit: {args[0]}: numeric argument required\n")
            sys.stderr.flush()
            shell_state.exit_code=1 # General Error
        except Exception as e:
            sys.stderr.write(f"exit: {e}\n")
            sys.stderr.flush()
            shell_state.exit_code = 1

    shell_state.running = False
    return shell_state.exit_code