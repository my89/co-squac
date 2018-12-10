import argparse
import sys
import json
import re
import random
import math


def parse_args():
  parser = argparse.ArgumentParser('Measure the percetage of sentences covered')
  parser.add_argument('--input_file', help='Input common format JSON file.', required=True)
  return parser.parse_args()

p = parse_args()
qfile = p.input_file
data = json.load(open(qfile))

covered_percentage = 0.0
t = 0
for _item in data["data"]:
  for i,_p in enumerate(_item["paragraphs"]):
    sents = _p["context"].replace("CANNOTANSWER","").split(".")
    _sents = []
    for s in sents:
      if len(s.strip()) == 0: continue
      _sents.append(s)
    sents = _sents
    covered = set()
    for _q in _p["qas"]:
       #try:
        if "orig_span" in _q: search = _q["orig_span"].split(".")[0]
        else: search = _q["orig_answer"]["text"].split(".")[0]
        if "CANNOTANSWER" in search or "unknown" in search: continue
        for _s in range(0,len(sents)):
          if search in sents[_s]: 
            covered.add(_s)
            t += 1
    covered_percentage += float(len(covered)) / len(sents)
print("contexts analyzed: {}, coverage (portion of sentences touched): {}".format(t, covered_percentage/t))

