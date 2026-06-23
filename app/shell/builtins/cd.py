# app/shell/builtins/cd.py
import os
import sys


def builtin_cd(args, shell_state) -> int:
    """
    Change the current working directory and update ShellState.cwd.

    Supported forms:
        cd          -> $HOME
        cd ~        -> $HOME
        cd .        -> stay (no-op)
        cd ..       -> parent dir
        cd ./rel    -> relative path
        cd /abs     -> absolute path
    """
    if not args:
        target = os.path.expanduser('~')
    else:
        given = args[0]
        if given == '~':
            target = os.path.expanduser('~')
        elif given == '.':
            shell_state.exit_code = 0
            return 0
        else:
            # os.path.abspath resolves both relative and absolute paths correctly
            # As well as ..
            target = os.path.abspath(given)

    try:
        os.chdir(target)
        shell_state.cwd = os.getcwd()   # keep ShellState in sync
        shell_state.exit_code = 0
    except FileNotFoundError:
        # label = args[0] if args else '~'    # Handle Empty space
        label = args[0]    # Handle Empty space
        sys.stderr.write(f"cd: {label}: No such file or directory\n")
        sys.stderr.flush()
        shell_state.exit_code = 1
    except NotADirectoryError:
        sys.stderr.write(f"cd: {args[0]}: Not a directory\n")
        sys.stderr.flush()
        shell_state.exit_code = 1
    except PermissionError:
        sys.stderr.write(f"cd: {args[0]}: Permission denied\n")
        sys.stderr.flush()
        shell_state.exit_code = 1

    return shell_state.exit_code