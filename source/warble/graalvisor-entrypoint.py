import sys
import os

sys.path.insert(0, os.environ['WARBLE_HOME'])
import warblecc

def warble(argv):
    sys.argv = [ "warblecc.py" ]
    for item in eval(argv):
        sys.argv.append(item)
    warblecc.main()

def main(args):
    try:
        return {"result": warble(args)}
    except Exception as e:
        return {"result": str(e)}
