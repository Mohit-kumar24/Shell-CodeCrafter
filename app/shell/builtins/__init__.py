# app/shell/builtins/__init__.py
from app.shell.builtins.cd       import builtin_cd
from app.shell.builtins.echo     import builtin_echo
from app.shell.builtins.exit     import builtin_exit
from app.shell.builtins.pwd      import builtin_pwd
from app.shell.builtins.type_cmd import builtin_type

# Dict gives O(1) builtin lookup in executor.
# HOOK: add "history", "jobs", "declare" here when those stages are reached.
BUILTIN_COMMANDS = {
    "cd":   builtin_cd,
    "echo": builtin_echo,
    "exit": builtin_exit,
    "pwd":  builtin_pwd,
    "type": builtin_type,
}