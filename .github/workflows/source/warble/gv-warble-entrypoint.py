import sys
import os
import io
from contextlib import redirect_stdout

sys.path.insert(0, os.environ['WARBLE_HOME'])
import warblecc

def warble(argv):
    sys.argv = [ "warblecc.py" ]
    for item in eval(argv):
        sys.argv.append(item)
    f = io.StringIO()
    with redirect_stdout(f):
        warblecc.main()
    return f.getvalue()

def main(args):
    try:
        return {"result": warble(args)}
    except Exception as e:
        return {"result": str(e)}
