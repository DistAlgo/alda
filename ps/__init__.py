from .ps import PS, PS_LOCAL, PS_CLASS, PS_GLOBAL, CODE, AST

ps = PS()

__all__ = [ps, PS_LOCAL, PS_CLASS, PS_GLOBAL, AST, CODE]

# try export ps directly
# change constants to
# ps.FORMAT_AST
# ps.FORMAT_CODE
