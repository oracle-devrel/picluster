#!/usr/bin/python3

import os
import argparse


if __name__ == '__main__':
    df = pd.read_csv ('scraped_tweets.csv', usecols= ['username', 'text'])
    #print(df)

    for index, row in df.iterrows():
        print(row['username'])

        text = row['text']
        print(text)
        text = text.replace("#BiGPiClusterInMyGarage", "")
        text = text.strip()
        print(text)

        if text[0] == '{' and text[-1] == '}':
            print("we have code")
            #TODO send code to a Pi
