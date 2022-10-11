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

             ["var1", "python3 warblecc.py -v \"{r=10;PRINT(r)}\"", "10"],
             ["var2", "python3 warblecc.py -v \"{r=10*2;PRINT(r)}\"", "20"],
             ["var3", "python3 warblecc.py -v \"{r=10+2;PRINT(r)}\"", "12"],
             ["var4", "python3 warblecc.py -v \"{r=8^2;PRINT(r)}\"", "64"],

             ["paran1", "python3 warblecc.py -v \"{k=4*10+2;PRINT(k)}\"", "42"],
             ["paran2", "python3 warblecc.py -v \"{k=(4*10+2);PRINT(k)}\"", "42"],
             ["paran3", "python3 warblecc.py -v \"{k=4*(10+2);PRINT(k)}\"", "48"],

             ["iftest1", "python3 warblecc.py -v \"{a=10*3;IF(1<2){PRINT(a)}}\"", "30"],
             ["ifelsetest1", "python3 warblecc.py -v \"{a=10*3;IF(a<10){PRINT(a)}ELSE{PRINT(\\\"sonic screwdriver\\\")}}\"", "sonic screwdriver"],

             ["whiletest1", "python3 warblecc.py -v \"{i=0;WHILE(i<10){PRINT(i);i++}}\"", ""],
             ["whiletest2", "python3 warblecc.py -v \"{i=10;WHILE(i>0){PRINT(i);i--}}\"", ""],

             ["fortest1", "python3 warblecc.py -v \"{FOR(i=0;i<10;i++){PRINT(i)}}\"", ""],

             #["dectest1", "python3 warblecc.py -v "{FUNCTION foo(x, y){VAR i=10;WHILE(i>0){PRINT(i);i--}}}"''"
             ["drawtest1", "python3 warblecc.py -v \"{DRAW(1+1,1-1,2,3,4)}\"", ""],
             ["drawtest2", "python3 warblecc.py -v \"{x=1;DRAWLINE(1+1,1-1,x,x,2,3,4)}\"", ""],

             ["func1", "python3 warblecc.py -v \"{PRINT(ROUND(ACOS(0.0),3))}\"", "1.571"],
             ["func2", "python3 warblecc.py -v \"{PRINT(2*ROUND(ACOS(0.0),3))}\"", "3.142"],
             ["func3", "python3 warblecc.py -v \"{r=ROUND(ACOS(0.0),3);PRINT(r)}\"", "1.571"],
             ["func4", "python3 warblecc.py -v \"{r=ROUND(ACOS(0.0),3);r=r*2;PRINT(r)}\"", "3.142"],

             ["forx1", "python3 warblecc.py -v \"{k=2;x=16.0^k;PRINT(x)}\"", "256.0"],
             ["forx2", "python3 warblecc.py -v \"{k=2;x=16.0^k*(10+2);PRINT(x)}\"", "256"],
             ["forx3", "python3 warblecc.py -v \"{k=2;x=16^k;PRINT(x)}\"", "256"],
             ["forx4", "python3 warblecc.py -v \"{k=1;x=1/16.0^2*(4.0/(8*k+1));PRINT(x)}\"", ""],
             ["forx5", "python3 warblecc.py -v \"{k=1;x=(8*k+1);PRINT(x)}\"", ""],
             ["forx6", "python3 warblecc.py -v \"{k=1;x=(4.0/(8*k+1));PRINT(x)}\"", ""],
             ["forx7", "python3 warblecc.py -v \"{k=1;x=2*(4.0/(8*k+1));PRINT(x)}\"", ""],
             ["forx8", "python3 warblecc.py -v \"{x=2^(3+1);PRINT(x)}\"", ""],
             ["forx12", "python3 warblecc.py -v \"{k=1;x=1/16.0^2*(4.0/(8*k+1)-2.0/(8*k+4)-1.0/(8*k+5)-1.0/(8*k+6));PRINT(x)}\"", "0.0005055708180708181"],
             ["forx13", "python3 warblecc.py -v \"{x=0;SETPRECISION(10);FOR(k=0;k<10;k++){x=x+(1/16.0^k*(4.0/(8*k+1)-2.0/(8*k+4)-1.0/(8*k+5)-1.0/(8*k+6)))};PRINT(x)}\"", ""]
            ]

    for test in TESTS:
        if testname == None:
            runTest(test)
        elif test[0] == testname:
            runTest(test)

main()
