import sys
import enum
import utils

# Lexer object keeps track of current position in the source code and produces each token.
class Lexer:
    def __init__(self, input):
        self.source = input + '\n' # Source code to lex as a string. Append a newline to simplify lexing/parsing the last token/statement.
        self.curChar = ''          # Current character in the string.
        self.curPos = -1           # Current position in the string.
        self.nextChar()


    # Process the next character.
    def nextChar(self):
        self.curPos += 1
        if len(self.source) <= self.curPos:
            self.curChar = '\0'  # EOF
        else:
            self.curChar = self.source[self.curPos]


    # Return the next character without adjusting the current character position.
    def peek(self):
        if len(self.source) <= self.curPos + 1:
            return '\0'
        return self.source[self.curPos+1]


    def skipWhitespace(self):
        while self.curChar == ' ' or self.curChar == '\t' or self.curChar == '\r':
            #print('whitespace ' + self.curChar)
            self.nextChar()


    # Invalid token found, print error message and exit.
    def abort(self, message):
        sys.exit("Lexing error. " + message)


    # Return the next token.
    def getToken(self):
        self.skipWhitespace()
        token = None

        # Check the first character of this token to see if we can decide what it is.
        # If it is a multiple character operator (e.g., !=), number, identifier, or keyword, then we will process the rest.
        if self.curChar == '=':
            # Check whether this token is = or ==
            if self.peek() == '=':
                lastChar = self.curChar
                self.nextChar()
                token = Token(lastChar + self.curChar, TokenType.EQEQ)
            else:
                token = Token(self.curChar, TokenType.EQ)
        elif self.curChar == '+':
            # Check whether this token is + or ++
            if self.peek() == '+':
                lastChar = self.curChar
                self.nextChar()
                token = Token(lastChar + self.curChar, TokenType.PLUSPLUS)
            else:
                token = Token(self.curChar, TokenType.PLUS)
        elif self.curChar == '-':
            # Check whether this token is - or --
            if self.peek() == '-':
                lastChar = self.curChar
                self.nextChar()
                token = Token(lastChar + self.curChar, TokenType.MINUSMINUS)
            else:
                token = Token(self.curChar, TokenType.MINUS)
        elif self.curChar == '*':
            token = Token(self.curChar, TokenType.ASTERISK)
        elif self.curChar == '/':
            token = Token(self.curChar, TokenType.SLASH)
        elif self.curChar == '%':
            token = Token(self.curChar, TokenType.MODULOUS)
        elif self.curChar == '>':
            if self.peek() == '=':
                lastChar = self.curChar
                self.nextChar()
                token = Token(lastChar + self.curChar, TokenType.GTEQ)
            else:
                token = Token(self.curChar, TokenType.GT)
        elif self.curChar == '<':
            if self.peek() == '=':
                lastChar = self.curChar
                self.nextChar()
                token = Token(lastChar + self.curChar, TokenType.LTEQ)
            else:
                token = Token(self.curChar, TokenType.LT)
        elif self.curChar == '!':
            if self.peek() == '=':
                lastChar = self.curChar
                self.nextChar()
                token = Token(lastChar + self.curChar, TokenType.NOTEQ)
            else:
                self.abort("Expected !=, got !" + self.peek())
        elif self.curChar == ';':
            token = Token(self.curChar, TokenType.SEPARATOR)
        elif self.curChar == '(':
            token = Token(self.curChar, TokenType.BEGIN)
        elif self.curChar == ')':
            token = Token(self.curChar, TokenType.END)
        elif self.curChar == '{':
            token = Token(self.curChar, TokenType.BEGIN_BLOCK)
        elif self.curChar == '}':
            token = Token(self.curChar, TokenType.END_BLOCK)
        elif self.curChar == ',':
            token = Token(self.curChar, TokenType.COMMA)
        elif self.curChar == '\n':
            token = Token('\n', TokenType.NEWLINE)
        elif self.curChar == '\0':
            token = Token('', TokenType.EOF)
        elif self.curChar == '\"':
            self.nextChar()
            startPos = self.curPos
            while self.curChar != '\"':
                if self.curChar == '\r' or self.curChar == '\n' or self.curChar == '\t' or self.curChar == '\\' or self.curChar == '%':
                    self.abort("Illegal character in string.")
                self.nextChar()

            tokText = self.source[startPos : self.curPos] # Get the substring.
            token = Token(tokText, TokenType.STRING)

        elif self.curChar.isdigit():
            # Leading character is a digit, so this must be a number.
            # Get all consecutive digits and decimal if there is one.
            startPos = self.curPos
            while self.peek().isdigit():
                self.nextChar()
            if self.peek() == '.': # Decimal!
                self.nextChar()

                # Must have at least one digit after decimal.
                if not self.peek().isdigit():
                    # Error!
                    self.abort("Illegal character in number.")
                while self.peek().isdigit():
                    self.nextChar()

            tokText = self.source[startPos : self.curPos + 1] # Get the substring.
            token = Token(tokText, TokenType.NUMBER)

        elif self.curChar.isalpha():
            # Leading character is a letter, so this must be an identifier or a keyword.
            # Get all consecutive alpha numeric characters.
            startPos = self.curPos

            while self.peek().isalnum():
                self.nextChar()

            # Check if the token is in the list of keywords.
            tokText = self.source[startPos : self.curPos + 1] # Get the substring.
            keyword = Token.checkIfKeyword(tokText)
            if keyword == None: # Identifier
                token = Token(tokText, TokenType.IDENT)
                utils.debug('ident ' + tokText)
            else:   # Keyword
                token = Token(tokText, keyword)
                utils.debug('keyword ' + tokText)

        else:
            self.abort("Unknown token: " + self.curChar)

        self.nextChar()
        utils.debug("DEBUG " + token.text)
        return token



# Token contains the original text and the type of token.
class Token:
    def __init__(self, tokenText, tokenKind):
        self.text = tokenText   # The token's actual text. Used for identifiers, strings, and numbers.
        self.kind = tokenKind   # The TokenType that this token is classified as.

    @staticmethod
    def checkIfKeyword(tokenText):
        for kind in TokenType:
            # Relies on all keyword enum values being 1XX.
            if kind.name == tokenText and 100 < kind.value and kind.value < 500:
                return kind
        return None

    @staticmethod
    def checkIfFunction(tokenText):
        for kind in TokenType:
            # Relies on all keyword enum values being 1XX.
            if kind.name == tokenText and 300 <= kind.value:
                return kind
        return None

    @staticmethod
    def checkIfFunctionWithResult(tokenText):
        for kind in TokenType:
            # Relies on all keyword enum values being 1XX.
            if kind.name == tokenText and 400 < kind.value and kind.value < 500:
                return kind
        return None


# TokenType is our enum for all the types of tokens.
class TokenType(enum.Enum):
    EOF = -1
    NEWLINE = 0
    NUMBER = 1
    IDENT = 2
    STRING = 3
    BEGIN_BLOCK = 4
    END_BLOCK = 5
    BEGIN = 6
    END = 7

    # Keywords.
    #FUN = 101
    VAR = 105
    IF = 106
    ELSE = 107
    WHILE = 109
    FOR = 110

    # Operators.
    EQ = 201
    PLUS = 202
    MINUS = 203
    ASTERISK = 204
    SLASH = 205
    MODULOUS = 206
    EQEQ = 220
    NOTEQ = 221
    LT = 222
    LTEQ = 223
    GT = 224
    GTEQ = 225
    COMMA = 226
    SEPARATOR = 227
    PLUSPLUS = 228
    MINUSMINUS = 229

    # Functions.
    PRINT = 320
    LOG = 321
    DRAW = 322
    DRAWLINE = 323

    PLAYSOUND = 390
    LIGHTS = 391

    # Functions with returns values
    ROUND = 401
    ACOS = 402
