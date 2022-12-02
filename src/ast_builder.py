from typing import Any

from lark import Token, Transformer

import nodes as xdnodes




import sys
from typing import List
from dataclasses import dataclass

from lark import Lark, ast_utils, Transformer, v_args
from lark.tree import Meta

this_module = sys.modules[__name__]



class AstBuilder(Transformer):
    def LITERAL(self, item: Token) -> xdnodes.LiteralExprNode:
        return xdnodes.LiteralExprNode(item.line, item.column, int(item.value))

    def expr(self, items: list[Any]) -> xdnodes.ExprNode:
        return items[0]

    def return_stmt(self, items: list[Any]) -> xdnodes.ReturnStmtNode:
        expr = items[1]
        return xdnodes.ReturnStmtNode(expr.line, expr.column, expr)

    def block(self, items: list[Any]) -> xdnodes.BlockNode:
        statements = items[1:-1]
        return xdnodes.BlockNode(items[0].line, items[0].column, statements)

    def func_def(self, items: list[Any]) -> xdnodes.FuncDefNode:
        type = items[0].value
        identifier = items[1].value
        body = items[2]
        return xdnodes.FuncDefNode(
            items[0].line, items[0].column, type, identifier, body
        )

    def program(self, items: list[Any]) -> xdnodes.ProgramNode:
        return xdnodes.ProgramNode(0, 0, items)



class _Ast(ast_utils.Ast):
    # This will be skipped by create_transformer(), because it starts with an underscore
    pass

class _Statement(_Ast):
    # This will be skipped by create_transformer(), because it starts with an underscore
    pass

@dataclass
class Value(_Ast, ast_utils.WithMeta):
    "Uses WithMeta to include line-number metadata in the meta attribute"
    meta: Meta
    value: object

@dataclass
class Name(_Ast):
    name: str

@dataclass
class CodeBlock(_Ast, ast_utils.AsList):
    # Corresponds to code_block in the grammar
    statements: List[_Statement]

@dataclass
class If(_Statement):
    cond: Value
    then: CodeBlock

@dataclass
class SetVar(_Statement):
    # Corresponds to set_var in the grammar
    name: str
    value: Value

@dataclass
class Print(_Statement):
    value: Value


class ToAst(Transformer):
    # Define extra transformation functions, for rules that don't correspond to an AST class.

    def STRING(self, s):
        # Remove quotation marks
        return s[1:-1]

    def DEC_NUMBER(self, n):
        return int(n)

    @v_args(inline=True)
    def start(self, x):
        return x

#
#   Define Parser
#
