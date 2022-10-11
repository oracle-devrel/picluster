#!/usr/bin/python3

import os
import argparse
import pandas as pd


#,username,description,location,following,followers,totaltweets,retweetcount,text,hashtags,created_at

tag = "#pi"


if __name__ == '__main__':

    filename = 'scraped_tweets%s.csv'
    lfilename = ""

    # i = 0
    # while os.path.exists(filename % i):
    #     lfilename = filename % i
    #     print(lfilename)
    #     i += 1

    i = 0

    while True:
        lfilename = filename % i
        print(lfilename)
        if os.path.exists(filename % i):
            break
        i += 1

    print(lfilename)

    df = pd.read_csv(lfilename)#, usecols= ['username', 'text'])

    for index, row in df.iterrows():
        #print(row['username'])

        text = row['text']
        code = text.replace(tag, "").strip()

        if code[0] == '{' and code[-1] == '}':
            print("we have code")
            #TODO send code to a Pi
            print(row['username'])
            print(code)
