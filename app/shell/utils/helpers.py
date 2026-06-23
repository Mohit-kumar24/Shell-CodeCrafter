# app/shell/utils/helpers.py
import os


def is_builtin(name, builtin_commands):
    """O(1) dict lookup — True if name is a registered builtin."""
    return name in builtin_commands


def find_in_path(name):
    """
    Search each directory in $PATH for an executable named `name`.
    Returns the full path string on success, None if not found.
    Time: O(d) where d = number of dirs in PATH.
    
    * os.pathsep = Delmiiter (: or ;)
    """
    path_env = os.environ.get('PATH', '')
    for directory in path_env.split(os.pathsep):
        if not directory:
            continue
        full_path = os.path.join(directory, name)
        if os.path.isfile(full_path) and os.access(full_path, os.X_OK):
            return full_path
    return None