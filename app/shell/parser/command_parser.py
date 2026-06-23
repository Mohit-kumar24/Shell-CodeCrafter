# app/shell/parser/command_parser.py
from app.shell.parser.tokens import WORD, PIPE, REDIRECT_OUT, REDIRECT_APPEND, REDIRECT_IN, REDIRECT_ERR, EOF


def parse(tokens):
    """
    Convert token list into a command dict.

    Returns:
        {
            "command":   str,   # argv[0]
            "args":      list,  # argv[1:]
            "redirects": list,  # HOOK Stage 4: [(REDIRECT_TYPE, target), ...]
            "pipeline":  list,  # HOOK Stage 4: [cmd_dict, ...] for | chains
        }
    Returns None for empty/whitespace-only input.

    Stage 1-3: only WORD tokens are acted on.
    Stage 4:   un-comment redirect + pipeline branches below.
    """
    _REDIRECT_TYPES = {REDIRECT_OUT, REDIRECT_APPEND, REDIRECT_IN, REDIRECT_ERR}

    command   = None
    args      = []
    redirects = []   # HOOK Stage 4
    pipeline  = []   # HOOK Stage 4

    i = 0
    while i < len(tokens):
        tok_type, tok_val = tokens[i]

        if tok_type == EOF:
            break

        if tok_type == WORD:
            if command is None:
                command = tok_val
            else:
                args.append(tok_val)
            i += 1
            continue

        # HOOK Stage 4 — redirect: consume (redirect_token, target_word)
        if tok_type in _REDIRECT_TYPES:
            if i + 1 < len(tokens) and tokens[i + 1][0] == WORD:
                redirects.append((tok_type, tokens[i + 1][1]))
                i += 2
            else:
                i += 1
            continue

        # HOOK Stage 4 — pipeline: split here into sub-command dicts
        if tok_type == PIPE:
            # pipeline.append({"command": command, "args": args, "redirects": redirects})
            # command, args, redirects = None, [], []
            i += 1
            continue

        i += 1

    if command is None:
        return None

    return {
        "command":   command,
        "args":      args,
        "redirects": redirects,
        "pipeline":  pipeline,
    }