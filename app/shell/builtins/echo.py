# app/shell/builtins/echo.py
import sys


def builtin_echo(args, shell_state) -> int:
    """Print args joined by a single space, followed by newline."""
    # HOOK Stage 2: handle -n flag (suppress newline) here
    # HOOK Stage 5: $VAR expansion arrives pre-expanded via lexer/parser
    try:
        sys.stdout.write(' '.join(args) + '\n')
        sys.stdout.flush()
        shell_state.exit_code = 0
    except Exception as e:
        sys.stderr.write(f"echo: {e}\n")
        sys.stderr.flush()
        shell_state.exit_code = 1
    return shell_state.exit_code