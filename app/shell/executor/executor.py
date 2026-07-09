# app/shell/executor/executor.py
import subprocess
import sys
from app.shell.core.state import shell_state
from app.shell.parser.lexer import tokenize
from app.shell.parser.command_parser import parse
from app.shell.builtins import BUILTIN_COMMANDS
from app.shell.redirection.redirector import apply_redirects, restore_redirects


def process_command(raw_command):
    """
    Full pipeline: raw string -> tokenize -> parse -> redirection and pipeline -> dispatch
    """
    # Removing '\n' inserted due to readline
    command = raw_command.strip()
    if not command:
        return

    
    tokens = tokenize(command)

    cmd_dict = parse(tokens)
    if cmd_dict is None:
        return

    cmd_name = cmd_dict["command"]
    args     = cmd_dict["args"]
    redirects = cmd_dict["redirects"]
    
    # HOOK Stage 4: handle pipeline here (chain subprocess stdin/stdout)

    # handle redirects here (open fds, dup2) before running
    saved_fds, opened_files = [], []
    if redirects:
        try:
            saved_fds, opened_files = apply_redirects(redirects)
        except (IOError, OSError) as e:
            sys.stderr.write(f"Redirect Error : {e}\n")
            sys.stderr.flush()
            shell_state.exit_code = 1
            return

    try:
        # Dispatch: O(1) builtin check, else external
        if cmd_name in BUILTIN_COMMANDS:
            BUILTIN_COMMANDS[cmd_name](args, shell_state)
        else:
            _run_external(cmd_name, args)
    finally:
        # Always restore fds — even if the command crashed  
        if redirects:
            restore_redirects(saved_fds, opened_files)


def _run_external(cmd_name, args):
    """Fork + exec an external binary found via $PATH."""
    # HOOK Stage 4: accept stdin/stdout fd params for pipeline support
    try:
        result = subprocess.run(
            [cmd_name] + args,
            cwd=shell_state.cwd,
        )
        shell_state.exit_code = result.returncode

    except FileNotFoundError:
        sys.stderr.write(f"{cmd_name}: command not found\n")
        sys.stderr.flush()
        shell_state.exit_code = 127

    except Exception as e:
        sys.stderr.write(f"Error : {cmd_name}: {e}\n")
        sys.stderr.flush()
        shell_state.exit_code = 1