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

        self.username = None

        self.nextToken()
        self.nextToken()    # Call this twice to initialize current and peek.


    def incIndent(self):
        utils.debug("incIndent")
        self.indent += 3


    def decIndent(self):
        utils.debug("decIndent")
        self.indent -= 3


    def getIndent(self):
        result = ''
        count = 0
        while (count < self.indent):
            count = count + 1
            result += ' '
        return result


    def setUsername(self, v):
        self.username = v


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

        if self.username is not None:
            self.emitter.emitLine("warbleapi.setUsername({})".format(self.username))

        self.emitter.emitLine("def main():")
        self.incIndent()
        self.parseBlock()
        self.decIndent()
        self.emitter.emitLine("main()")


    def parseBlock(self):
        utils.debug('parseBlock {}'.format(self.curToken.text))
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
        utils.debug('parseStatement {}'.format(self.curToken.text))
        # Check the first token to see what kind of statement this is.

        # IF ( comparison ) block
        if self.checkToken(TokenType.IF):
            self.nextToken()
            self.match(TokenType.BEGIN)
            self.emitter.emit(self.getIndent() + "if (")
            self.parseComparison()
            self.match(TokenType.END)
            self.emitter.emitLine("):")
            self.incIndent()
            self.parseBlock()
            self.decIndent()
            if self.checkToken(TokenType.ELSE):
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
            self.emitter.emit(self.getIndent() + variable + " = ")

            self.match(TokenType.IDENT)
            self.match(TokenType.EQ)
            self.parseExpression()
            self.emitter.emitLine("")

            self.match(TokenType.SEPARATOR)

            self.emitter.emit(self.getIndent() + "while (")
            self.parseComparison()

            self.match(TokenType.SEPARATOR)
            self.emitter.emitLine("):")
            self.incIndent()

            savedCode = self.parseExpression(False)
            self.match(TokenType.END)

            self.parseBlock()
            self.emitter.emitLine(self.getIndent() + savedCode)
            self.decIndent()

        # IDENT ++ | --
        elif self.checkToken(TokenType.IDENT):
            self.emitter.emit(self.getIndent() + self.curToken.text)

            if self.curToken.text not in self.symbols:
                self.symbols.add(self.curToken.text)
            self.nextToken()

            if self.checkToken(TokenType.EQ):
                self.nextToken()
                self.emitter.emit("=")
                self.parseExpression()
                self.emitter.emitLine("")
            else:
                self.parseIncOperator()

        else:
            # Functions
            if lex.Token.checkIfFunction(self.curToken.text):
                self.parseFunction()
            # This is not a valid statement. Error!
            else:
                self.abort("Invalid statement at " + self.curToken.text + " (" + self.curToken.kind.name + ")")

    def parseFunction(self, newline = True):
        utils.debug('parseFunction {}'.format(self.curToken.text))
        # PRINT ( expression | string )
        if self.checkToken(TokenType.PRINT):
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
                self.emitter.emit(")")
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

        elif self.checkToken(TokenType.ACOS):
            self.nextToken()
            self.emitter.emit(self.getIndent() + "warbleapi.acos(")
            self.match(TokenType.BEGIN)
            self.parseExpression()
            self.emitter.emit(")")
            self.match(TokenType.END)

        elif self.checkToken(TokenType.SETPRECISION):
            self.nextToken()
            self.emitter.emit(self.getIndent() + "warbleapi.setPrecision(")
            self.match(TokenType.BEGIN)
            self.parseExpression()
            self.emitter.emit(")")
            self.match(TokenType.END)

        elif self.checkToken(TokenType.ROUND):
            self.nextToken()
            self.emitter.emit(self.getIndent() + "warbleapi.round(")
            self.match(TokenType.BEGIN)
            functionTypes = [self.parseExpression, self.parseExpression]
            self.parseArguments(functionTypes);
            self.emitter.emit(")")


        # DRAW ( expression, expression, expression, expression, expression )
        elif self.checkToken(TokenType.DRAW):
            self.nextToken()

            if self.checkToken(TokenType.BEGIN):
                self.nextToken()
                self.emitter.emit(self.getIndent() + "warbleapi.draw(")
                functionTypes = [self.parseExpression, self.parseExpression, self.parseExpression, self.parseExpression, self.parseExpression]
                self.parseArguments(functionTypes);
                self.emitter.emit(")")

        # DRAWLINE ( expression, expression, expression, expression, expression, expression, expression )
        elif self.checkToken(TokenType.DRAWLINE):
            self.nextToken()

            if self.checkToken(TokenType.BEGIN):
                self.nextToken()
                self.emitter.emit(self.getIndent() + "warbleapi.drawline(")
                functionTypes = [self.parseExpression, self.parseExpression, self.parseExpression, self.parseExpression, self.parseExpression, self.parseExpression, self.parseExpression]
                self.parseArguments(functionTypes);
                self.emitter.emit(")")

        # SLEEP ( expression, expression, expression, expression )
        elif self.checkToken(TokenType.SLEEP):
            self.nextToken()

            if self.checkToken(TokenType.BEGIN):
                self.nextToken()
                self.emitter.emit(self.getIndent() + "warbleapi.sleep(")
                functionTypes = [self.parseExpression, self.parseExpression, self.parseExpression, self.parseExpression]
                self.parseArguments(functionTypes);
                self.emitter.emit(")")

        # LIGHTS ( expression, expression, expression, expression )
        elif self.checkToken(TokenType.LIGHTS):
            self.nextToken()

            if self.checkToken(TokenType.BEGIN):
                self.nextToken()
                self.emitter.emit(self.getIndent() + "warbleapi.lights(")
                functionTypes = [self.parseExpression, self.parseExpression, self.parseExpression, self.parseExpression]
                self.parseArguments(functionTypes);
                self.emitter.emit(")")

        # PLAYSOUND ( string )
        elif self.checkToken(TokenType.PLAYSOUND):
            self.nextToken()
            self.match(TokenType.BEGIN)
            url = self.curToken.text
            self.match(TokenType.STRING)
            self.match(TokenType.END)
            self.emitter.emit(self.getIndent() + "warbleapi.play_sound(\"" + url + "\")\n")

        # SETDATA ( string, string )
        elif self.checkToken(TokenType.SETDATA):
            self.nextToken()
            self.match(TokenType.BEGIN)
            name = self.curToken.text
            self.match(TokenType.STRING)
            value = self.curToken.text
            self.match(TokenType.IDENT)
            self.match(TokenType.END)
            self.emitter.emit(self.getIndent() + "warbleapi.setData({}, {})\n".format(name, value))

        # GETDATA ( string )
        elif self.checkToken(TokenType.GETDATA):
            self.nextToken()
            self.match(TokenType.BEGIN)
            name = self.curToken.text
            self.match(TokenType.STRING)
            self.match(TokenType.END)
            self.emitter.emit(self.getIndent() + "warbleapi.getData({})\n".format(name))

        # SAVE ( string, string )
        elif self.checkToken(TokenType.SAVE):
            self.nextToken()
            self.match(TokenType.BEGIN)
            name = self.curToken.text
            self.match(TokenType.STRING)
            value = self.curToken.text
            self.match(TokenType.IDENT)
            self.match(TokenType.END)
            self.emitter.emit(self.getIndent() + "warbleapi.save({}, {})\n".format(name, value))

        # LOAD ( string )
        elif self.checkToken(TokenType.LOAD):
            self.nextToken()
            self.match(TokenType.BEGIN)
            name = self.curToken.text
            self.match(TokenType.STRING)
            self.match(TokenType.END)
            self.emitter.emit(self.getIndent() + "warbleapi.getData({})\n".format(name))


        if newline == True:
            self.emitter.emitLine("")

    def parseIncOperator(self):
        utils.debug('parseIncOperator {}'.format(self.curToken.text))
        ident = self.prevToken.text
        if self.checkToken(TokenType.PLUSPLUS):
            self.nextToken()
            self.emitter.emitLine(" = {} + 1".format(ident, ident))
        elif self.checkToken(TokenType.MINUSMINUS):
            self.nextToken()
            self.emitter.emitLine(" = {} - 1".format(ident, ident))

    def parseArguments(self, args):
        utils.debug('parseArguments {}'.format(self.curToken.text))
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
        utils.debug('parseComparison {}'.format(self.curToken.text))
        self.parseExpression()

        # Must be at least one comparison operator and another expression.
        if self.isComparisonOperator():
            self.emitter.emit(self.curToken.text)
            self.nextToken()
            self.parseExpression()


    # expression ::= term {( "-" | "+" | "^" | "*" | "/" | IDENT | FUNCTION ) term}
    def parseExpression(self, print=True):
        utils.debug('parseExpression {}'.format(self.curToken.text))
        nested_count = 0
        savedCode = ""
        while (True):
            if lex.Token.checkIfFunctionWithResult(self.curToken.text):
                self.decIndent()
                self.parseFunction(newline = False)
                self.incIndent()
            elif self.checkToken(TokenType.CAROT):
                self.emitter.emit('**')
                self.nextToken()
            elif self.checkToken(TokenType.PLUS) or self.checkToken(TokenType.MINUS):
                self.emitter.emit(self.curToken.text)
                self.nextToken()
            elif self.checkToken(TokenType.ASTERISK) or self.checkToken(TokenType.SLASH):
                self.emitter.emit(self.curToken.text)
                self.nextToken()
            elif self.checkToken(TokenType.BEGIN):
                self.emitter.emit(self.curToken.text)
                self.nextToken()
                nested_count = nested_count + 1
            elif self.checkToken(TokenType.END) and nested_count > 0:
                self.emitter.emit(self.curToken.text)
                self.nextToken()
                nested_count = nested_count - 1
            elif self.checkToken(TokenType.NUMBER):
                self.parsePrimary()
            elif self.checkToken(TokenType.IDENT) and self.checkPeek(TokenType.PLUSPLUS):
                ident = self.curToken.text
                self.nextToken()
                self.nextToken()
                if print:
                    self.emitter.emitLine("{} = {} + 1".format(ident, ident))
                else:
                    savedCode = "{} = {} + 1".format(ident, ident)
            elif self.checkToken(TokenType.IDENT) and self.checkPeek(TokenType.MINUSMINUS):
                ident = self.curToken.text
                self.nextToken()
                self.nextToken()
                if print:
                    self.emitter.emitLine("{} = {} - 1".format(ident, ident))
                else:
                    self.emitter.emitLine("{} = {} - 1".format(ident, ident))
            elif self.checkToken(TokenType.IDENT):
                self.parsePrimary()
            else:
                break

        if nested_count > 0:
            abort("unmatched parentheses")

        if print == False:
            return savedCode

    # primary ::= number | ident
    def parsePrimary(self):
        utils.debug('parsePrimary {}'.format(self.curToken.text))
        if lex.Token.checkIfFunctionWithResult(self.curToken.text):
            self.decIndent()
            self.parseFunction(newline = False)
            self.incIndent()
        elif self.checkToken(TokenType.NUMBER):
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
