# app/shell/builtins/type_cmd.py
import sys
from app.shell.utils.helpers import find_in_path


def builtin_type(args, shell_state) -> int:
    """
    Identify how each name would be interpreted.
    Output format (matches bash):
        echo is a shell builtin
        cat is /usr/bin/cat
        xyz: not found
    """
    if not args:
        sys.stderr.write("type: missing argument\n")
        sys.stderr.flush()
        shell_state.exit_code = 1
        return shell_state.exit_code

    # Lazy import avoids circular import at module load time:
    # incomplete module in sys cache causing error
    # builtins/__init__.py imports type_cmd, type_cmd imports BUILTIN_COMMANDS
    # only when builtin_type() is *called* (by which time __init__ is fully loaded).
    from app.shell.builtins import BUILTIN_COMMANDS

    exit_code = 0
    for name in args:
        if name in BUILTIN_COMMANDS:
            sys.stdout.write(f"{name} is a shell builtin\n")
        else:
            path = find_in_path(name)
            if path:
                sys.stdout.write(f"{name} is {path}\n")
            else:
                sys.stdout.write(f"{name}: not found\n")
                exit_code = 1

    sys.stdout.flush()
    shell_state.exit_code = exit_code
    return exit_code