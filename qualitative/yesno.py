import argparse
import sys
import json
import re
import random
import math

def parse_args():
  parser = argparse.ArgumentParser('Count the percenntage of instances with yes/no answers')
  parser.add_argument('--input_file', help='Input JSON file in common data format.', required=True)
  return parser.parse_args()
 
p = parse_args()
qfile = p.input_file
data = json.load(open(qfile))

yn = 0.0
t = 0
for _item in data["data"]:
  for i,_p in enumerate(_item["paragraphs"]):
    for _q in _p["qas"]:
      t += 1
      if  _q['yesno'] == "y" or _q['yesno'] == "n": yn +=1 
print("portion of instances with a yes/no answer: {}".format(yn/t))

  
