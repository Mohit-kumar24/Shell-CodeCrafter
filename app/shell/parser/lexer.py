# app/shell/parser/lexer.py
from app.shell.parser.tokens import (
    WORD, PIPE, REDIRECT_OUT, REDIRECT_APPEND,
    REDIRECT_IN, REDIRECT_ERR, EOF,
)

# Characters that always end a WORD token
_WORD_TERMINATORS = frozenset(' \t\n|><')


def _read_word(s, start, n):
    """
    Consume one WORD from s[start:], handling quotes and backslash escapes.
    Returns (word_string, chars_consumed).

    HOOK (Stage 2): single-quote and double-quote logic lives here.
    HOOK (Stage 5): $VAR expansion should be added inside double-quote branch.
    """
    word = []
    i = start

    while i < n and s[i] not in _WORD_TERMINATORS:
        ch = s[i]

        # --- single quote: preserve every character literally ---
        # HOOK Stage 2: this is intentionally minimal; no expansions inside ''
        if ch == "'":
            i += 1
            while i < n and s[i] != "'":
                word.append(s[i])
                i += 1
            if i < n:
                i += 1          # skip closing '
            continue

        # --- double quote: allow backslash escape, no $VAR yet ---
        # HOOK Stage 5: add $VAR expansion inside here
        if ch == '"':
            i += 1
            while i < n and s[i] != '"':
                if s[i] == '\\' and i + 1 < n and s[i + 1] in ('"', '\\', '$', '\n'):
                    word.append(s[i + 1])
                    i += 2
                else:
                    word.append(s[i])
                    i += 1
            if i < n:
                i += 1          # skip closing "
            continue

        # --- backslash outside quotes ---
        # HOOK Stage 2: extend escape table here (\n, \t, etc.)
        if ch == '\\' and i + 1 < n:
            word.append(s[i + 1])
            i += 2
            continue

        word.append(ch)
        i += 1

    return (''.join(word), i - start)


def tokenize(input_string):
    """
    Convert raw input string into a list of (token_type, value) tuples.

    Data-structure note: we use a plain list as a stack/queue for the
    caller (command_parser) to consume left-to-right in O(n) time.
    """
    tokens = []
    s = input_string.rstrip('\n')
    n = len(s)
    i = 0

    while i < n:
        c = s[i]

        # --- whitespace: skip ---
        if c in (' ', '\t'):
            i += 1
            continue

        # --- pipe  HOOK Stage 4 ---
        if c == '|':
            tokens.append((PIPE, '|'))
            i += 1
            continue

        # --- >> or >  HOOK Stage 4 ---
        if c == '>':
            if i + 1 < n and s[i + 1] == '>':
                tokens.append((REDIRECT_APPEND, '>>'))
                i += 2
            else:
                tokens.append((REDIRECT_OUT, '>'))
                i += 1
            continue

        # --- <  HOOK Stage 4 ---
        if c == '<':
            tokens.append((REDIRECT_IN, '<'))
            i += 1
            continue

        # --- 2> or 2>>  HOOK Stage 4 ---
        # Only treat as redirect when '2' is the very start of a new token
        if c == '2' and i + 1 < n and s[i + 1] == '>':
            if i + 2 < n and s[i + 2] == '>':
                tokens.append((REDIRECT_ERR, '2>>'))
                i += 3
            else:
                tokens.append((REDIRECT_ERR, '2>'))
                i += 2
            continue

        # --- WORD (handles quotes + escapes inside _read_word) ---
        word, consumed = _read_word(s, i, n)
        i += consumed
        if word:
            tokens.append((WORD, word))

    tokens.append((EOF, ''))
    return tokens