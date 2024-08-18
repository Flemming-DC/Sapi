from sqlglot import *
from sqlglot.parser import Parser

sapi = ""
tokens = []
dialect_str = "postgres"

# dette skiller tokenizing og parsing ad
d = Dialect(dialect_str)
tokens = d.tokenize(sapi)
asts = d.parser().parse(tokens, sapi)




