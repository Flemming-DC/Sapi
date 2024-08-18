import sqlparse
from sqlparse.sql import Token, Statement

sql = "SELECT * FROM users WHERE id = 1; select 1"
statements: tuple[Statement] = sqlparse.parse(sql)
tokens: list[Token] = statements[0].tokens
# print(tokens)
for token in tokens:
    token.is_group()
    print(token)
