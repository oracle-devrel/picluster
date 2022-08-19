import sys
import lex
import emit
import utils

from lex import TokenType

# Parser object keeps track of current token, checks if the code matches the grammar, and emits code along the way.
class Parser:
    def __init__(self, lexer, emitter):
        self.indent = 0
        self.lexer = lexer
        self.emitter = emitter

        self.symbols = set()        # All variables that have been declared so far.

        self.prevToken = None
        self.curToken = None
        self.peekToken = None
        self.nextToken()
        self.nextToken()    # Call this twice to initialize current and peek.


    def incIndent(self):
        self.indent += 3


    def decIndent(self):
        self.indent -= 3


    def getIndent(self):
        result = ''
        count = 0
        while (count < self.indent):
            count = count + 1
            result += ' '
        return result


    # Return true if the current token matches.
    def checkToken(self, kind):
        return kind == self.curToken.kind


    # Return true if the next token matches.
    def checkPeek(self, kind):
        return kind == self.peekToken.kind


    # Try to match current token. If not, error. Advances the current token.
    def match(self, kind):
        if not self.checkToken(kind):
            self.abort("Expected " + kind.name + ", got " + self.curToken.kind.name)
        self.nextToken()


    # Advances the current token.
    def nextToken(self):
        self.prevToken = self.curToken
        self.curToken = self.peekToken
        self.peekToken = self.lexer.getToken()
        # No need to worry about passing the EOF, lexer handles that.


    # Return true if the current token is a comparison operator.
    def isComparisonOperator(self):
        return self.checkToken(TokenType.GT) or self.checkToken(TokenType.GTEQ) or self.checkToken(TokenType.LT) or self.checkToken(TokenType.LTEQ) or self.checkToken(TokenType.EQEQ) or self.checkToken(TokenType.NOTEQ)


    def abort(self, message):
        utils.debug("Error! " + message)
        sys.exit("Error! " + message)


    # Production rules.

    # program ::= {statement}
    def program(self):
        self.emitter.headerLine("#!/usr/bin/python3")
        self.emitter.emitLine("import warbleapi")

        while self.checkToken(TokenType.NEWLINE):
            self.nextToken()

        self.emitter.emitLine("def main():")
        self.incIndent()
        self.parseBlock()
        self.decIndent()
        self.emitter.emitLine("main()")


    def parseBlock(self):
        if self.checkToken(TokenType.BEGIN_BLOCK):
            self.nextToken()

            # Parse all the statements in the program.
            while not self.checkToken(TokenType.EOF):
                self.parseStatement()

                if self.checkToken(TokenType.SEPARATOR):
                    self.nextToken()

                if self.checkToken(TokenType.END_BLOCK):
                    self.nextToken()
                    break


    # One of the following statements...
    def parseStatement(self):
        # Check the first token to see what kind of statement this is.

        # "VAR" ident = expression
        if self.checkToken(TokenType.VAR):
            self.nextToken()
            #  Check if ident exists in symbol table. If not, declare it.
            if self.curToken.text not in self.symbols:
                self.symbols.add(self.curToken.text)

            self.emitter.emit(self.getIndent() + self.curToken.text + " = ")
            self.match(TokenType.IDENT)
            self.match(TokenType.EQ)

            self.parseExpression()
            self.emitter.emitLine('')

            if self.checkToken(TokenType.SEPARATOR):
                self.nextToken()

        # IF ( comparison ) block
        elif self.checkToken(TokenType.IF):
            self.nextToken()
            self.match(TokenType.BEGIN)
            self.emitter.emit(self.getIndent() + "if (")
            self.parseComparison()
            self.match(TokenType.END)
            self.emitter.emitLine("):")
            self.incIndent()
            self.parseBlock()
            self.decIndent()
            utils.debug("here " + self.curToken.text)
            if self.checkToken(TokenType.ELSE):
                utils.debug("here " + self.curToken.text)
                self.nextToken()
                self.emitter.emitLine(self.getIndent() + "else:")
                self.incIndent()
                self.parseBlock()
                self.decIndent()

        # WHILE ( comparison ) block
        elif self.checkToken(TokenType.WHILE):
            self.nextToken()
            self.match(TokenType.BEGIN)
            self.emitter.emit(self.getIndent() + "while (")
            self.parseComparison()
            self.match(TokenType.END)
            self.emitter.emitLine("):")
            self.incIndent()
            self.parseBlock()
            self.decIndent()

        # FOR ( identifier = AssignmentExpression ; comparison ; expression ) block
        elif self.checkToken(TokenType.FOR):
            self.nextToken()
            self.match(TokenType.BEGIN)

            #  Check if ident exists in symbol table. If not, declare it.
            if self.curToken.text not in self.symbols:
                self.symbols.add(self.curToken.text)

            variable = self.curToken.text
            utils.debug('dude ' + variable)
            self.emitter.emit(self.getIndent() + variable + " = ")

            self.match(TokenType.IDENT)
            self.match(TokenType.EQ)
            self.parseExpression()
            self.emitter.emitLine("")

            self.match(TokenType.SEPARATOR)


            self.emitter.emit(self.getIndent() + "while (")
            utils.debug('dude')
            self.parseComparison()

            self.match(TokenType.SEPARATOR)
            self.emitter.emitLine("):")
            self.incIndent()

            self.emitter.emit(self.getIndent())
            self.parseExpression()
            self.emitter.emitLine("")
            self.match(TokenType.END)

            self.parseBlock()
            self.decIndent()

        # IDENT ++ | --
        elif self.checkToken(TokenType.IDENT):
            self.emitter.emit(self.getIndent() + self.curToken.text)
            self.nextToken()
            self.parseIncOperator()

        # Functions

        # PRINT ( expression | string )
        elif self.checkToken(TokenType.PRINT):
            self.nextToken()
            self.match(TokenType.BEGIN)
            utils.debug(self.curToken.kind)
            if self.checkToken(TokenType.STRING):
                text = self.curToken.text
                self.nextToken()
                self.match(TokenType.END)
                self.emitter.emitLine(self.getIndent() + "print(\"{}\")".format(text))
            else:
                self.emitter.emit(self.getIndent() + "print(")
                self.parseExpression()
                self.emitter.emitLine(")")
                self.match(TokenType.END)

        # LOG ( expression | string )
        elif self.checkToken(TokenType.LOG):
            self.nextToken()
            self.match(TokenType.BEGIN)
            utils.debug(self.curToken.kind)
            if self.checkToken(TokenType.STRING):
                text = self.curToken.text
                self.nextToken()
                self.match(TokenType.END)
                self.emitter.emitLine(self.getIndent() + "warbleapi.log(\"{}\")".format(text))
            else:
                self.emitter.emit(self.getIndent() + "warbleapi.log(")
                self.parseExpression()
                self.emitter.emitLine(self.getIndent() + ")")
                self.match(TokenType.END)

        # DRAW ( expression, expression, expression, expression, expression )
        elif self.checkToken(TokenType.DRAW):
            self.nextToken()

            if self.checkToken(TokenType.BEGIN):
                self.nextToken()
                self.emitter.emit(self.getIndent() + "warbleapi.draw(")
                functionTypes = [self.parseExpression, self.parseExpression, self.parseExpression, self.parseExpression, self.parseExpression]
                self.parseArguments(functionTypes);
                self.emitter.emitLine(")")

        # DRAWLINE ( expression, expression, expression, expression, expression, expression, expression )
        elif self.checkToken(TokenType.DRAWLINE):
            self.nextToken()

            if self.checkToken(TokenType.BEGIN):
                self.nextToken()
                self.emitter.emit(self.getIndent() + "warbleapi.drawline(")
                functionTypes = [self.parseExpression, self.parseExpression, self.parseExpression, self.parseExpression, self.parseExpression, self.parseExpression, self.parseExpression]
                self.parseArguments(functionTypes);
                self.emitter.emitLine(")")

        # LIGHTS ( expression, expression, expression, expression )
        elif self.checkToken(TokenType.LIGHTS):
            self.nextToken()

            if self.checkToken(TokenType.BEGIN):
                self.nextToken()
                self.emitter.emit(self.getIndent() + "warbleapi.lights(")
                functionTypes = [self.parseExpression, self.parseExpression, self.parseExpression, self.parseExpression]
                self.parseArguments(functionTypes);
                self.emitter.emitLine(")")

        # PLAYSOUND ( string )
        elif self.checkToken(TokenType.PLAYSOUND):
            self.nextToken()
            self.match(TokenType.BEGIN)
            url = self.curToken.text
            self.match(TokenType.STRING)
            self.match(TokenType.END)
            self.emitter.emitLine(self.getIndent() + "warbleapi.play_sound(\"" + url + "\")\n")

        # This is not a valid statement. Error!
        else:
            self.abort("Invalid statement at " + self.curToken.text + " (" + self.curToken.kind.name + ")")

    def parseIncOperator(self):
        #utils.debug("dd")
        #if self.prevToken.kind.
        #utils.debug("here")
        ident = self.prevToken.text
        if self.checkToken(TokenType.PLUSPLUS):
            self.nextToken()
            self.emitter.emitLine(" = {} + 1".format(ident, ident))
        elif self.checkToken(TokenType.MINUSMINUS):
            self.nextToken()
            self.emitter.emitLine(" = {} - 1".format(ident, ident))

    def parseArguments(self, args):
        for argParserFunction in args:
            argParserFunction()
            if self.checkToken(TokenType.END):
                self.nextToken()
                break
            elif self.checkToken(TokenType.COMMA):
                self.emitter.emit(", ")
                self.nextToken()

    # comparison ::= expression (("==" | "!=" | ">" | ">=" | "<" | "<=") expression)+
    def parseComparison(self):
        self.parseExpression()

        # Must be at least one comparison operator and another expression.
        if self.isComparisonOperator():
            self.emitter.emit(self.curToken.text)
            self.nextToken()
            self.parseExpression()
        # Can have 0 or more comparison operator and expressions.
        while self.isComparisonOperator():
            self.emitter.emit(self.curToken.text)
            self.nextToken()
            self.parseExpression()


    # expression ::= term {( "-" | "+" ) term}
    def parseExpression(self):
        self.parseTerm()

        # Can have 0 or more +/- and expressions.
        while self.checkToken(TokenType.PLUS) or self.checkToken(TokenType.MINUS):
            self.emitter.emit(self.curToken.text)
            self.nextToken()
            self.parseTerm()


    # term ::= unary {( "/" | "*" ) unary}
    def parseTerm(self):
        self.parseUnary()
        # Can have 0 or more *// and expressions.
        while self.checkToken(TokenType.ASTERISK) or self.checkToken(TokenType.SLASH):
            self.emitter.emit(self.curToken.text)
            self.nextToken()
            self.parseUnary()


    # unary ::= ["+" | "-"] primary
    def parseUnary(self):
        # Optional unary +/-
        if self.checkToken(TokenType.PLUS) or self.checkToken(TokenType.MINUS):
            self.emitter.emit(self.curToken.text)
            self.nextToken()
        self.parsePrimary()
        if self.checkToken(TokenType.PLUSPLUS) or self.checkToken(TokenType.MINUSMINUS):
            self.parseIncOperator()


    # primary ::= number | ident
    def parsePrimary(self):
        if self.checkToken(TokenType.NUMBER):
            self.emitter.emit(self.curToken.text)
            self.nextToken()
        elif self.checkToken(TokenType.IDENT):
            # Ensure the variable already exists.
            if self.curToken.text not in self.symbols:
                self.abort("Referencing variable before assignment: " + self.curToken.text)

            self.emitter.emit(self.curToken.text)
            self.nextToken()
        else:
            # Error!
            self.abort("Unexpected token at " + self.curToken.text)
