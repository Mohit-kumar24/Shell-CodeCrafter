# app/shell/executor/executor.py
import subprocess
import sys
from app.shell.core.state import shell_state
from app.shell.parser.lexer import tokenize
from app.shell.parser.command_parser import parse
from app.shell.builtins import BUILTIN_COMMANDS


def process_command(raw_command):
    """
    Full pipeline: raw string → tokenize → parse → dispatch.

    HOOK Stage 4: after parse(), check cmd_dict["redirects"] and
                  cmd_dict["pipeline"] before dispatching.
    """
    # Removing '\n' inserted due to readline
    command = raw_command.strip()
    if not command:
        return

    # --- Stage 2: lex ---
    tokens = tokenize(command)

    # --- Stage 3: parse ---
    cmd_dict = parse(tokens)
    if cmd_dict is None:
        return

    cmd_name = cmd_dict["command"]
    args     = cmd_dict["args"]

    # HOOK Stage 4: handle redirects here (open fds, dup2) before running
    # HOOK Stage 4: handle pipeline here (chain subprocess stdin/stdout)

    # --- Dispatch: O(1) builtin check, else external ---
    if cmd_name in BUILTIN_COMMANDS:
        BUILTIN_COMMANDS[cmd_name](args, shell_state)
    else:
        _run_external(cmd_name, args)


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
        sys.stderr.write(f"pysh: {cmd_name}: {e}\n")
        sys.stderr.flush()
        shell_state.exit_code = 1