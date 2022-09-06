#!/usr/bin/python3

from pydub import AudioSegment
from pydub.playback import play
import argparse
import wget

# pip install wget
# pip install playsound

parser = argparse.ArgumentParser(description='Example: python3 playsound.py --url http://downloads.bbc.co.uk/doctorwho/sounds/tardis.mp3')
parser.add_argument('--url', type=str, help='URL of mp3 to play')
args = parser.parse_args()
url = args.url

filename = wget.download(url)
sound = AudioSegment.from_file_using_temporary_files(filename)
play(sound)
if os.path.exists(filename):
    print("exists")
    os.remove(filename)
