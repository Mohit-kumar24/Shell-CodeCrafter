# app/shell/redirection/redirector.py
import os
import sys
from app.shell.parser.tokens import (
    REDIRECT_OUT, REDIRECT_APPEND,
    REDIRECT_IN,  REDIRECT_ERR,
)

# ==============================================================================
# SHELL REDIRECTION ARCHITECTURES: PROS & CONS
# ==============================================================================
#
# 1. IN-PROCESS FD SWAPPING (Current Architecture)
#    - How it works: Parent overwrites its own FDs with os.dup2, runs the 
#      command, then restores original FDs from backups.
#    - Pros: Necessary for shell "built-ins" (like `cd` or `exit`) that must 
#      modify or execute within the parent process.
#    - Cons: Risky. If the restore step fails, the parent shell's I/O is 
#      permanently broken and the shell becomes unusable.
#
# 2. FORK-EXEC MODEL (POSIX Standard / Real Shells like Bash)
#    - How it works: Parent clones itself via os.fork(). Only the child changes 
#      its FDs, then replaces itself with the target program via os.exec().
#    - Pros: Process isolation. Extremely safe because the parent's FDs are 
#      never touched, eliminating the need for a "restore" function.
#    - Cons: More complex. Requires manual child process management (PIDs, 
#      waitpid, handling zombie processes).
#
# 3. SUBPROCESS ROUTER (High-Level Python Standard)
#    - How it works: Uses Python's `subprocess.run()`, passing Python file 
#      objects directly (e.g., stdout=file_obj).
#    - Pros: Clean, robust, and the module handles all OS plumbing for you.
#    - Cons: Abstracts away the low-level OS mechanics, defeating the purpose 
#      of building a custom OS-level shell from scratch.
# ==============================================================================

def apply_redirects(redirects):
    """
    For each (tok_type, tok_val, target) in redirects:
      - save a copy of the original fd with os.dup()
      - open the target file
      - point the original fd at the file with os.dup2()

    Returns (saved_fds, opened_files) so the caller can restore later.

    Why os.dup / os.dup2 and not just reassigning sys.stdout?
    os.dup2 works at the C file-descriptor level, so it covers:
      * builtins that write via sys.stdout / sys.stderr
      * subprocesses that inherit fd 1 / fd 2 from the shell process
    Reassigning sys.stdout would only fix Python-level writes.

    HOOK Stage 4 (pipeline): this same function will be called per-segment
    once pipeline support replaces stdin/stdout fds between processes.
    
    # Note: 'fds' (file descriptors) are OS-level integer IDs for data streams.
    # 0 = stdin (input), 1 = stdout (output), 2 = stderr (errors).
    # We manipulate these so external processes inherit the redirected streams.
    
    
    """
    saved_fds    = []   # [(fd_number, saved_copy_fd), ...]
    opened_files = []   # file objects — closed in restore_redirects()

    for tok_type, tok_val, target in redirects:
        try:
            if tok_type == REDIRECT_OUT:
                # > target  ->  truncate/create, bind to stdout (fd 1)
                f = open(target, 'w')
                # Creating a backup of o/p screen
                saved_fds.append((1, os.dup(1)))
                os.dup2(f.fileno(), 1)
                opened_files.append(f)

            elif tok_type == REDIRECT_APPEND:
                # >> target  ->  append, bind to stdout (fd 1)
                f = open(target, 'a')
                saved_fds.append((1, os.dup(1)))
                #  Getting OS index of a file and unplugging from 1 to given fileno
                os.dup2(f.fileno(), 1)
                opened_files.append(f)

            elif tok_type == REDIRECT_IN:
                # < target  ->  read, bind to stdin (fd 0)
                f = open(target, 'r')
                saved_fds.append((0, os.dup(0)))
                os.dup2(f.fileno(), 0)
                opened_files.append(f)

            elif tok_type == REDIRECT_ERR:
                # 2> or 2>>  ->  bind to stderr (fd 2)
                # tok_val tells us which: "2>" = truncate, "2>>" = append
                mode = 'a' if tok_val == '2>>' else 'w'
                f = open(target, mode)
                saved_fds.append((2, os.dup(2)))
                os.dup2(f.fileno(), 2)
                opened_files.append(f)

        except (IOError, OSError):
            # Back Up if something goes wrong to fix shell to previous state
            restore_redirects(saved_fds, opened_files)
            raise

    return saved_fds, opened_files


def restore_redirects(saved_fds, opened_files):
    """
    Put the original fds back.  Must be called in a finally block.

    Reversed order matters: if the same fd was redirected twice
    (unusual but valid), we undo the last change first.
    """
    for fd, saved_copy in reversed(saved_fds):
        os.dup2(saved_copy, fd)
        os.close(saved_copy)     # release the temporary copy

    for f in opened_files:
        try:
            f.close()
        except OSError:
            pass