# app/shell/parser/lexer.py
from app.shell.parser.tokens import (
    WORD, PIPE, REDIRECT_OUT, REDIRECT_APPEND,
    REDIRECT_IN, REDIRECT_ERR, EOF,
)

# Characters that always end a WORD token
_WORD_TERMINATORS = frozenset(' \t\n|><')


def _read_word(s, start, n):
    """
    Consume one WORD from s[start:], handling Single / Double quotes and backslash escapes.
    Returns (word_string, chars_consumed).

    HOOK (Stage 2): single-quote and double-quote logic lives here.
    HOOK (Stage 5): $VAR expansion should be added inside double-quote branch.
    """
    word = []
    i = start
    quote_state = None  # Tracks if we are inside quotes: None, "'", or '"'

    while i < n:
        ch = s[i]

        # --- Check if we need to exit or change quote states first ---
        if quote_state == "'":
            if ch == "'":
                quote_state = None
                i += 1  # skip closing '
                continue
            word.append(ch)
            i += 1
            continue

        elif quote_state == '"':
            if ch == '"':
                quote_state = None
                i += 1  # skip closing "
                continue
            
            # Add $VAR expansion inside here
            # (Stage 5 hook placeholder: check for '$' here if needed later)
            
            if ch == '\\' and i + 1 < n and s[i + 1] in ('"', '\\', '$', '\n'):
                word.append(s[i + 1])
                i += 2
                continue
            else:
                word.append(ch)
                i += 1
                continue

        # --- Handling outside of quotes ---
        if ch in _WORD_TERMINATORS:
            break

        # --- single quote: preserve every character literally ---
        if ch == "'":
            quote_state = "'"
            i += 1
            continue

        # --- double quote: allow backslash escape, no $VAR yet ---
        if ch == '"':
            quote_state = '"'
            i += 1
            continue

        # --- backslash outside quotes ---
        # extend escape table here (\n, \t, etc.)
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

        # --- pipe  ---
        if c == '|':
            tokens.append((PIPE, '|'))
            i += 1
            continue

        # --- >> or > ---
        if c == '>':
            if i + 1 < n and s[i + 1] == '>':
                tokens.append((REDIRECT_APPEND, '>>'))
                i += 2
            else:
                tokens.append((REDIRECT_OUT, '>'))
                i += 1
            continue

        # --- <   ---
        if c == '<':
            tokens.append((REDIRECT_IN, '<'))
            i += 1
            continue
        
        # --- 1> or 1>>  ---
        if c == '1' and i + 1 < n and s[i + 1] == '>':
            if i + 2 < n and s[i + 2] == '>':
                tokens.append((REDIRECT_APPEND, '>>'))  # Normalizing token value to >>
                i += 3
            else:
                tokens.append((REDIRECT_OUT, '>'))      # Normalizing token value to >
                i += 2
            continue

        # --- 2> or 2>>  ---
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