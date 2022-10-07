# Emitter object keeps track of the generated code and outputs it.

import os

class Emitter:
    def __init__(self, fullPath):
        self.fullPath = fullPath
        self.header = ""
        self.code = ""

    def emit(self, code):
        self.code += code

    def emitLine(self, code):
        self.code += code + '\n'

    def headerLine(self, code):
        self.header += code + '\n'

    def writeFile(self):
        stat = os.statvfs('../warble')
        readonly = bool(stat.f_flag & os.ST_RDONLY)

        if not readonly:
            with open(self.fullPath, 'w') as outputFile:
                outputFile.write(self.header + self.code)

    def run(self):
        exec(self.code)
