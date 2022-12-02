import parser
import rich
from pathlib import Path
import typer,sys

from lark import Lark, ast_utils, Transformer, v_args, lexer

#from parser import Parser
import ast_builder as ast

this_module = sys.modules[__name__]

app = typer.Typer()

global newcode
global end
newcode=""
end=True

@app.command()
def build():
    pass



def func(typz):
    funcSTR=""
    if len(typz) >= 2:
        ztype  = typz[1]
        name   = typz[0]
        params = []
        if len(typz) % 2 == 0 and len(typz) >= 4:
            for zl in range(2, len(typz)):
                if (zl % 2) == 0:
                    params.append([typz[zl], typz[zl + 1]])
            formParms = ""
            formP = []
            for itx in params:
                formP.append(itx[0] + ":" + itx[1])
            formParms = ','.join(formP)
            funcSTR = f'def {name}({formParms}) -> {ztype}:\n'.replace("string", "str")
        else:
            formParms=""
            funcSTR = f'def {name}({formParms}) -> {ztype}:\n'.replace("string", "str")
    else:
        return None
    if end:
        global newcode
        newcode+=funcSTR
        return newcode



def conv(treez):
    newcode = ""
    ca = treez
    for it in ca.children:
        typz = []
        call=True
        if type(it) == lexer.Token:
            continue
        for iti in it.children:
            vtype = it.data
            if vtype == "func_def":
                end=False
                if type(iti) == lexer.Token:
                    typz.append(iti.value)
            if vtype=="func_call":
                if '"' in it.children[0]:
                    break
                z = it.children
                funcc = z[0]
                params=z
                del params[0]
                callSTR = ("\t" if tab else "") + f'{funcc}({",".join(params)})\n'
                newcode+=callSTR
                
        end=True
        z=func(typz)
        if z!=None:
            newcode=z
        if type(it) == lexer.Token:
            continue
        for iz in it.children:
            if type(iz) != lexer.Token:
                vtype = iz.data
                tab = False
                if vtype == "block":
                    tab = True

                for inz in it.children:
                    if type(inz) != lexer.Token:
                        for izc in inz.children:
                            if type(izc) != lexer.Token:
                                if izc.data == "var_def":
                                    ivv = izc.children
                                    ztype = ivv[1].replace("string", "str")
                                    name = ivv[0]
                                    value = ivv[2]
                                    varSTR = ("\t" if tab else "") + f'{name}:{ztype} = {value}\n'
                                    newcode+=varSTR
                                if izc.data == "var_redef":
                                    ivv = izc.children
                                    name = ivv[0]
                                    value = ivv[1]
                                    varSTR = ("\t" if tab else "") + f'{name} += {value}\n'
                                    newcode+=varSTR
                                
                                if izc.data == "print":
                                    ivv = izc.children
                                    value = ','.join(ivv)
                                    newcode+=("\t" if tab else "") + f'print({value})\n'

                                if izc.data == "zprint":
                                    ivv = izc.children
                                    value = ','.join(ivv)
                                    newcode+=("\t" if tab else "") + f'print({value}, end ="")\n'

                    

                    if type(inz) != lexer.Token:
                        for z in inz.children:
                            if z == "}":
                                tab = False


        
    print(newcode)
    exec(newcode)

class EvalExpressions(Transformer):
    def expr(self, args):
            return eval(args[0])

@app.command(help="Compiles and runs.")
def run(input_file: Path):
    print(f"Compiling and running {input_file}")
    with input_file.open("rt") as f:
        parser = Lark(open("Grammar/grammar.lark", "r").read(), parser="lalr")
        transformer = ast_utils.create_transformer(this_module, ast.ToAst())
        tree = parser.parse(f.read())
        transformed = transformer.transform(tree)
        #rich.print(transformed)
        ca=EvalExpressions().transform( transformed )
        rich.print(ca)
        conv(ca)
        #tree = parser.parse(f.read())
    #rich.print(tree)
    #transformed = AstBuilder().transform(tree)
    #print(str(transformed.func_defs))
    #rich.print(transformed.func_defs)


def main():
    app()


if __name__ == "__main__":
    app()
