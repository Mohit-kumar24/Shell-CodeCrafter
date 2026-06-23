# app/shell/builtins/pwd.py
import sys


def builtin_pwd(args, shell_state) -> int:
    """Print the current working directory stored in ShellState."""
    # HOOK Stage 5: support -L (logical) / -P (physical) flags
    try:
        sys.stdout.write(shell_state.cwd + '\n')
        sys.stdout.flush()
        shell_state.exit_code = 0
    except Exception as e:
        # If sys.stdout is closed or not working properly
        sys.stderr.write(f"pwd: {e}\n")
        sys.stderr.flush()
        shell_state.exit_code = 1
    return shell_state.exit_code