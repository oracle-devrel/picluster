#!/usr/bin/python3

import argparse
import sys

import lex
import emit
import parser
import utils


# Run: python3 warblecc.py -v "{PRINT(\"test\")}"

def main():
    argparser = argparse.ArgumentParser(description='Warble is a Twitter Code Compiler')
    argparser.add_argument('code', type=str, help='Tweet')
    argparser.add_argument('-v', '--verbose', action='store_true')
    argparser.add_argument('-u', '--username', required=False, help='data paylod')
    args = argparser.parse_args()
    input = args.code
    username = args.username

    if args.verbose:
        utils.verbose = True

    utils.debug("INPUT: " + input)

    lexer = lex.Lexer(input)
    emitter = emit.Emitter("out.py")
    parse = parser.Parser(lexer, emitter)

    if username is not None:
        parse.setUsername(username)

    parse.program()
    emitter.writeFile()
    emitter.run()
    print("Transpiling complete.")

if __name__ == "__main__":
    main()
