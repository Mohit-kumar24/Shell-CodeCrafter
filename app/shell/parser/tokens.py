# app/shell/parser/tokens.py
# Token type constants — simple strings for O(1) identity checks

WORD            = "WORD"
PIPE            = "PIPE"            # |   HOOK: pipeline Stage 4
REDIRECT_OUT    = "REDIRECT_OUT"    # >   HOOK: redirection Stage 4
REDIRECT_APPEND = "REDIRECT_APPEND" # >>  HOOK: redirection Stage 4
REDIRECT_IN     = "REDIRECT_IN"     # <   HOOK: redirection Stage 4
REDIRECT_ERR    = "REDIRECT_ERR"    # 2>  HOOK: stderr redirect Stage 4
EOF             = "EOF"

# A token is a plain tuple: (TOKEN_TYPE, value_string)
# e.g. ("WORD", "echo"), ("PIPE", "|"), ("REDIRECT_OUT", ">")