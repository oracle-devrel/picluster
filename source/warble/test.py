#!/usr/bin/python3

import sys
import os
import argparse

# Run: python3 test.py

def abort(message):
    sys.exit("Error! " + message)

def runTest(test):
    try:
        print('--------------------------------------------------------------------------------')
        print('Running: ' + test[0])
        print('Command: ' + test[1])

        print("COMPILING")
        output = os.popen(test[1])
        output = output.read()
        print(output)

        print("RUNNING")

        if output.strip().find("Transpiling complete.") != -1:
            output = os.popen('python3 out.py')
            output = output.read()
            print("OUTPUT")
            print(output)

            if output.strip().find(test[2]) != -1:
                print("SUCCESS")
            else:
                abort("FAILED {}".format(test[0]))
        else:
            print("ERROR RUNNING")

        print('--------------------------------------------------------------------------------')
    except:
        print("ERROR")

def main():
    argparser = argparse.ArgumentParser(description='Warble Test Harness')
    argparser.add_argument('-t', '--testname', required=False, help='Test to run')
    args = argparser.parse_args()
    testname = args.testname

    # Tests array:
    # Name of test, Command to execute (remember to escape " and \), Expected results if any
    TESTS = [["printtest1", "python3 warblecc.py -v \"{PRINT(\\\"test\\\")}\"", "test"],
             ["printtest2", "python3 warblecc.py -v \"{PRINT(40)}\"", "40"],
             ["printtest3", "python3 warblecc.py -v \"PRINT(10+10)}\"}\"", "20"],
             ["playsoundtest1", "python3 warblecc.py -v \"{PLAYSOUND(\\\"tardis.mp3\\\");}\"", ""],
             ["playsoundtest3", "python3 warblecc.py -v \"{PLAYSOUND(\\\"http://downloads.bbc.co.uk/doctorwho/sounds/tardis.mp3\\\");}\"", ""],
             ["varioustest4", "python3 warblecc.py -v \"{LIGHTS(1+1,2,3,4);LOG(\\\"error\\\");LOG(10*99);PRINT(40);PRINT(10+10)}}\"", ""],


             ["iftest1", "python3 warblecc.py -v \"{VAR a=10*3;IF(1<2){PRINT(a)}}\"", "30"],
             ["ifelsetest1", "python3 warblecc.py -v \"{VAR a=10*3;IF(a<10){PRINT(a)}ELSE{PRINT(\\\"sonic screwdriver\\\")}}\"", "sonic screwdriver"],

             ["whiletest1", "python3 warblecc.py -v \"{VAR i=0;WHILE(i<10){PRINT(i);i++}}\"", ""],
             ["whiletest2", "python3 warblecc.py -v \"{VAR i=10;WHILE(i>0){PRINT(i);i--}}\"", ""],
             #["dectest1", "python3 warblecc.py -v "{FUNCTION foo(x, y){VAR i=10;WHILE(i>0){PRINT(i);i--}}}"''"
             ["drawtest1", "python3 warblecc.py -v \"{DRAW(1+1,1-1,2,3,4)}\"", ""],
             ["drawtest2", "python3 warblecc.py -v \"{VAR x=1;DRAWLINE(1+1,1-1,x,x,2,3,4)}\"", ""]
            ]

    for test in TESTS:
        if testname == None:
            runTest(test)
        elif test[0].find(testname) != -1:
            runTest(test)

main()
